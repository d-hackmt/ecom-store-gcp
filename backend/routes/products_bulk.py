"""
Bulk product ingestion routes: JSON bulk-add and the Excel + images-zip bulk
upload pipeline. Single-product CRUD lives in products.py.
"""
import base64
import io
import mimetypes
import zipfile

import openpyxl
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends

from ..models import Product
from ..database import products_collection
from ..auth import require_admin

# Split so the read replica / write replica of the deployment can each mount only
# the half it serves. The monolith (main.py) mounts both. Bulk ingestion only
# ever writes, so it lives on the write side; read_router stays empty.
read_router = APIRouter(prefix="/products", tags=["Products"])
write_router = APIRouter(prefix="/products", tags=["Products"])


@write_router.post("/bulk")
def add_multiple_products(products_list: list[Product], admin_email: str = Depends(require_admin)):
    """
    Add multiple products at once via bulk operation.
    """
    product_list = [product.model_dump() for product in products_list]
    products_collection.insert_many(product_list)
    return {"message": "Multiple products added successfully"}


@write_router.post("/bulk-upload")
async def bulk_upload_products(
    excel_file: UploadFile = File(...),
    images_zip: UploadFile = File(...),
    admin_email: str = Depends(require_admin),
):
    """
    Bulk-add products from an Excel sheet plus a zip of images.

    The Excel sheet's first row must be a header containing (at minimum):
    name, description, price, category, image — with optional size, color.
    The 'image' column must contain the exact filename of the matching image
    inside the uploaded zip (e.g. "red-shirt.jpg"); folder structure in the
    zip is ignored and matching is case-insensitive.
    Rows with missing required fields or an unmatched image are skipped and
    reported back instead of failing the whole upload.
    """
    excel_bytes = await excel_file.read()
    try:
        workbook = openpyxl.load_workbook(io.BytesIO(excel_bytes), read_only=True, data_only=True)
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read the Excel file. Please upload a valid .xlsx file.")
    sheet = workbook.active
    rows = sheet.iter_rows(values_only=True)

    try:
        header = [str(h).strip().lower() if h is not None else "" for h in next(rows)]
    except StopIteration:
        raise HTTPException(status_code=400, detail="The Excel file is empty.")

    required_columns = ["name", "description", "price", "category", "image"]
    missing_columns = [c for c in required_columns if c not in header]
    if missing_columns:
        raise HTTPException(
            status_code=400,
            detail=f"Excel is missing required column(s): {', '.join(missing_columns)}",
        )

    zip_bytes = await images_zip.read()
    try:
        zip_file = zipfile.ZipFile(io.BytesIO(zip_bytes))
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Could not read the images file. Please upload a valid .zip file.")

    # Map lowercase filename (ignoring any folder structure) -> archive path
    image_lookup = {}
    for archive_name in zip_file.namelist():
        if archive_name.endswith("/"):
            continue
        basename = archive_name.rsplit("/", 1)[-1]
        if basename:
            image_lookup[basename.lower()] = archive_name

    products_to_insert = []
    errors = []

    for row_num, row in enumerate(rows, start=2):  # row 1 is the header
        if row is None or all(cell is None for cell in row):
            continue  # skip blank rows

        row_data = dict(zip(header, row))

        name = str(row_data.get("name") or "").strip()
        description = str(row_data.get("description") or "").strip()
        category = str(row_data.get("category") or "").strip()
        price_raw = row_data.get("price")
        image_filename = str(row_data.get("image") or "").strip()

        if not name or not description or not category or price_raw is None or not image_filename:
            errors.append({"row": row_num, "reason": "Missing one of the required fields (name, description, price, category, image)"})
            continue

        try:
            price = int(price_raw)
        except (TypeError, ValueError):
            errors.append({"row": row_num, "reason": f"Invalid price value: {price_raw!r}"})
            continue

        archive_path = image_lookup.get(image_filename.lower())
        if archive_path is None:
            errors.append({"row": row_num, "reason": f"Image '{image_filename}' not found in the uploaded zip"})
            continue

        image_bytes = zip_file.read(archive_path)
        content_type = mimetypes.guess_type(image_filename)[0] or "image/jpeg"
        base64_image = base64.b64encode(image_bytes).decode("utf-8")

        size_raw = str(row_data.get("size") or "M,L").strip()
        color_raw = str(row_data.get("color") or "Black").strip()

        products_to_insert.append({
            "name": name,
            "description": description,
            "price": price,
            "category": category,
            "size": [s.strip() for s in size_raw.split(",") if s.strip()],
            "color": [c.strip() for c in color_raw.split(",") if c.strip()],
            "image_data": base64_image,
            "image_content_type": content_type,
        })

    if products_to_insert:
        products_collection.insert_many(products_to_insert)

    return {
        "message": f"{len(products_to_insert)} product(s) added successfully.",
        "inserted": len(products_to_insert),
        "failed": len(errors),
        "errors": errors,
    }
