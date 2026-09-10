"""
Database configuration and MongoDB connection setup.

Importing this module performs no network I/O: ``MongoClient`` connects lazily,
and the unique-account indexes are created by :func:`ensure_indexes`, which the
app calls once on startup from its lifespan handler. This keeps the test suite
fully offline (the tests swap these collections for in-memory fakes).
"""
from pymongo import MongoClient

from .config import settings

MONGO_URI = settings.mongo_uri

# MongoClient does not connect until the first operation, so this is import-safe.
client = MongoClient(MONGO_URI)
db = client["ecommerce_db"]

users_collection = db["users"]
products_collection = db["products"]
orders_collection = db["orders"]
cart_collection = db["cart"]


def ensure_indexes() -> None:
    """
    Create the unique indexes that enforce one account per email and per
    username at the database level. Idempotent — safe to call on every startup.
    """
    users_collection.create_index("email", unique=True)
    users_collection.create_index("username", unique=True)
