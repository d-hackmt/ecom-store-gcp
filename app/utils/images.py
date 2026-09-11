"""
Shared helpers for images stored as base64 in MongoDB (product photos, avatars).
"""


def to_data_url(image_data: str, content_type: str) -> str:
    """Build a data: URL from base64 image data plus its content type."""
    return f"data:{content_type};base64,{image_data}"


def resolve_image_field(document: dict) -> None:
    """
    Mutate `document` in place: ensure `image` is a usable URL (either its
    existing http(s) URL, or a reconstructed data: URL from image_data /
    image_content_type), then strip the raw base64 fields from the document.
    """
    has_url = bool(document.get("image")) and str(document["image"]).startswith("http")
    if not has_url and document.get("image_data") and document.get("image_content_type"):
        document["image"] = to_data_url(document["image_data"], document["image_content_type"])
    document.pop("image_data", None)
    document.pop("image_content_type", None)
