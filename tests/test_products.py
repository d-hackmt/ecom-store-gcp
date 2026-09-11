"""
Tests for core product CRUD (products.py) and admin gating (backend/auth.py).
"""
import io


def test_get_products_starts_empty(client):
    res = client.get("/products")
    assert res.status_code == 200
    assert res.json() == []


def test_add_product_requires_admin(client):
    res = client.post(
        "/products",
        data={"name": "Shirt", "description": "desc", "price": "499", "category": "men"},
        files={"image": ("shirt.jpg", b"fakejpeg", "image/jpeg")},
    )
    assert res.status_code == 403


def test_add_product_wrong_email_is_forbidden(client):
    res = client.post(
        "/products",
        data={"name": "Shirt", "description": "desc", "price": "499", "category": "men"},
        files={"image": ("shirt.jpg", b"fakejpeg", "image/jpeg")},
        headers={"X-User-Email": "nobody@example.com"},
    )
    assert res.status_code == 403


def test_add_and_list_product_as_admin(client, admin_headers):
    res = client.post(
        "/products",
        data={"name": "Classic Shirt", "description": "desc", "price": "499", "category": "men", "size": "M,L", "color": "Black"},
        files={"image": ("shirt.jpg", b"fakejpeg", "image/jpeg")},
        headers=admin_headers,
    )
    assert res.status_code == 200

    res = client.get("/products")
    assert res.status_code == 200
    products = res.json()
    assert len(products) == 1
    product = products[0]
    assert product["name"] == "Classic Shirt"
    assert product["price"] == 499
    assert product["size"] == ["M", "L"]
    assert product["image"] == f"/products/{product['id']}/image"
    assert "image_data" not in product
    assert "image_content_type" not in product


def test_category_and_price_filters(client, admin_headers):
    client.post(
        "/products",
        data={"name": "Cheap Shirt", "description": "d", "price": "300", "category": "men"},
        files={"image": ("a.jpg", b"x", "image/jpeg")},
        headers=admin_headers,
    )
    client.post(
        "/products",
        data={"name": "Fancy Dress", "description": "d", "price": "3000", "category": "women"},
        files={"image": ("b.jpg", b"x", "image/jpeg")},
        headers=admin_headers,
    )

    res = client.get("/products", params={"category": "men"})
    assert [p["name"] for p in res.json()] == ["Cheap Shirt"]

    res = client.get("/products", params={"min_price": 1000})
    assert [p["name"] for p in res.json()] == ["Fancy Dress"]

    res = client.get("/products", params={"max_price": 500})
    assert [p["name"] for p in res.json()] == ["Cheap Shirt"]


def test_update_product(client, admin_headers):
    client.post(
        "/products",
        data={"name": "Old Name", "description": "d", "price": "500", "category": "men"},
        files={"image": ("a.jpg", b"x", "image/jpeg")},
        headers=admin_headers,
    )
    product_id = client.get("/products").json()[0]["id"]

    res = client.put(
        f"/products/{product_id}",
        data={"name": "New Name", "price": "999"},
        headers=admin_headers,
    )
    assert res.status_code == 200

    updated = client.get("/products").json()[0]
    assert updated["name"] == "New Name"
    assert updated["price"] == 999


def test_update_product_invalid_id(client, admin_headers):
    res = client.put("/products/not-a-real-id", data={"name": "X"}, headers=admin_headers)
    assert res.status_code == 400


def test_update_product_nonexistent(client, admin_headers):
    res = client.put("/products/000000000000000000000000", data={"name": "X"}, headers=admin_headers)
    assert res.status_code == 404


def test_update_product_no_fields_rejected(client, admin_headers):
    client.post(
        "/products",
        data={"name": "P", "description": "d", "price": "500", "category": "men"},
        files={"image": ("a.jpg", b"x", "image/jpeg")},
        headers=admin_headers,
    )
    product_id = client.get("/products").json()[0]["id"]
    res = client.put(f"/products/{product_id}", data={}, headers=admin_headers)
    assert res.status_code == 400


def test_update_product_rejects_json_body(client, admin_headers):
    """
    The endpoint is multipart/form-data only (matches POST /products). A JSON
    body carries no form fields, so it is rejected rather than silently ignored.
    """
    client.post(
        "/products",
        data={"name": "P", "description": "d", "price": "500", "category": "men"},
        files={"image": ("a.jpg", b"x", "image/jpeg")},
        headers=admin_headers,
    )
    product_id = client.get("/products").json()[0]["id"]
    res = client.put(f"/products/{product_id}", json={"name": "New"}, headers=admin_headers)
    assert res.status_code == 400
    assert client.get(f"/products/{product_id}").json()["name"] == "P"  # unchanged


def test_delete_product(client, admin_headers):
    client.post(
        "/products",
        data={"name": "To Delete", "description": "d", "price": "500", "category": "men"},
        files={"image": ("a.jpg", b"x", "image/jpeg")},
        headers=admin_headers,
    )
    product_id = client.get("/products").json()[0]["id"]

    res = client.delete(f"/products/{product_id}", headers=admin_headers)
    assert res.status_code == 200
    assert client.get("/products").json() == []


def test_delete_nonexistent_product(client, admin_headers):
    res = client.delete("/products/000000000000000000000000", headers=admin_headers)
    assert res.status_code == 404


def test_get_single_product(client, admin_headers):
    client.post(
        "/products",
        data={"name": "Solo", "description": "d", "price": "700", "category": "women"},
        files={"image": ("a.jpg", b"x", "image/jpeg")},
        headers=admin_headers,
    )
    product_id = client.get("/products").json()[0]["id"]

    res = client.get(f"/products/{product_id}")
    assert res.status_code == 200
    body = res.json()
    assert body["id"] == product_id
    assert body["name"] == "Solo"
    assert body["image"] == f"/products/{product_id}/image"
    assert "image_data" not in body


def test_get_product_image(client, admin_headers):
    client.post(
        "/products",
        data={"name": "Imaged", "description": "d", "price": "500", "category": "men"},
        files={"image": ("a.jpg", b"fakejpegbytes", "image/jpeg")},
        headers=admin_headers,
    )
    product_id = client.get("/products").json()[0]["id"]

    res = client.get(f"/products/{product_id}/image")
    assert res.status_code == 200
    assert res.content == b"fakejpegbytes"
    assert res.headers["content-type"] == "image/jpeg"


def test_get_product_image_not_found(client):
    res = client.get("/products/000000000000000000000000/image")
    assert res.status_code == 404


def test_get_single_product_not_found(client):
    res = client.get("/products/000000000000000000000000")
    assert res.status_code == 404


def test_get_single_product_invalid_id(client):
    res = client.get("/products/not-a-real-id")
    assert res.status_code == 400


def test_delete_all_products_requires_admin(client):
    res = client.delete("/products")
    assert res.status_code == 403


def test_delete_all_products_as_admin(client, admin_headers):
    client.post(
        "/products",
        data={"name": "A", "description": "d", "price": "1", "category": "men"},
        files={"image": ("a.jpg", b"x", "image/jpeg")},
        headers=admin_headers,
    )
    res = client.delete("/products", headers=admin_headers)
    assert res.status_code == 200
    assert client.get("/products").json() == []


def test_bulk_json_add_requires_admin(client):
    res = client.post("/products/bulk", json=[])
    assert res.status_code == 403


def test_bulk_json_add_as_admin(client, admin_headers):
    payload = [
        {
            "name": "Bulk Item",
            "description": "d",
            "price": 100,
            "category": "kids",
            "size": ["S"],
            "color": ["Red"],
            "image": "https://example.com/x.jpg",
        }
    ]
    res = client.post("/products/bulk", json=payload, headers=admin_headers)
    assert res.status_code == 200
    products = client.get("/products").json()
    assert len(products) == 1
    assert products[0]["image"] == "https://example.com/x.jpg"


def test_bulk_upload_excel_zip(client, admin_headers):
    openpyxl = __import__("openpyxl")
    import zipfile

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["name", "description", "price", "category", "size", "color", "image"])
    ws.append(["Good Row", "desc", 499, "men", "M,L", "Black", "shirt.jpg"])
    ws.append(["Bad Row", "desc", 599, "men", "M", "Red", "missing.jpg"])
    excel_buf = io.BytesIO()
    wb.save(excel_buf)

    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w") as zf:
        zf.writestr("shirt.jpg", b"fakejpegbytes")

    res = client.post(
        "/products/bulk-upload",
        files={
            "excel_file": ("products.xlsx", excel_buf.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
            "images_zip": ("images.zip", zip_buf.getvalue(), "application/zip"),
        },
        headers=admin_headers,
    )
    assert res.status_code == 200
    body = res.json()
    assert body["inserted"] == 1
    assert body["failed"] == 1
    assert "missing.jpg" in body["errors"][0]["reason"]

    products = client.get("/products").json()
    assert len(products) == 1
    assert products[0]["name"] == "Good Row"


def test_bulk_upload_requires_admin(client):
    res = client.post(
        "/products/bulk-upload",
        files={
            "excel_file": ("a.xlsx", b"not real", "application/octet-stream"),
            "images_zip": ("a.zip", b"not real", "application/zip"),
        },
    )
    assert res.status_code == 403

