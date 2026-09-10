"""
Shared shaping of MongoDB user documents for API responses.
"""
from .images import to_data_url


def public_user(user: dict) -> dict:
    """Shape a MongoDB user document for API responses (never leak password_hash)."""
    avatar = None
    if user.get("avatar_data") and user.get("avatar_content_type"):
        avatar = to_data_url(user["avatar_data"], user["avatar_content_type"])
    return {"username": user["username"], "email": user["email"], "avatar": avatar}
