"""
Pydantic request/response models.

Two groups:
  - Catalog & commerce: Product (bulk-JSON shape), Order, CartItem
  - Accounts: UserRegister, UserLogin, ProfileUpdate, AccountDelete, GoogleAuth

Note on images: single-product create/update (`POST`/`PUT /products`) is
multipart and does not use a model — the image is uploaded and stored as base64.
`Product` below is only the JSON bulk-add shape, where `image` is a URL string.
"""
from typing import List, Optional

from pydantic import BaseModel, Field


# --------------------------------------------------------------------------- #
# Catalog & commerce
# --------------------------------------------------------------------------- #

class Product(BaseModel):
    """One product in a `POST /products/bulk` JSON payload (image is a URL)."""
    name: str
    description: str
    price: int = Field(ge=0)
    category: str
    size: List[str]        # e.g. ["S", "M", "L", "XL"]
    color: List[str]       # e.g. ["Black", "Blue"]
    image: str             # image URL


class Order(BaseModel):
    """Order placement payload."""
    user_email: str
    product_name: str
    quantity: int = Field(ge=1)
    price: int = Field(ge=0)   # unit price at time of order


class CartItem(BaseModel):
    """Add-to-cart payload."""
    user_email: str
    product_name: str
    quantity: int = Field(ge=1)


# --------------------------------------------------------------------------- #
# Accounts
# --------------------------------------------------------------------------- #

class UserRegister(BaseModel):
    """Registration payload: plaintext password is hashed before storage."""
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    """Login payload: email or username, plus password."""
    identifier: str
    password: str


class ProfileUpdate(BaseModel):
    """Edit-profile payload — current_password re-verifies identity before any change."""
    current_email: str
    current_password: str
    new_username: Optional[str] = None
    new_email: Optional[str] = None
    new_password: Optional[str] = None


class AccountDelete(BaseModel):
    """Payload to permanently delete an account."""
    email: str
    password: str


class GoogleAuth(BaseModel):
    """Google Sign-In payload: the ID-token JWT from Google Identity Services."""
    credential: str
