"""
MongoDB connection.

Importing this module performs no network I/O: ``MongoClient`` connects lazily,
on the first operation. The POC only ever *reads* the product catalog, so this
exposes a single collection handle and creates no indexes.
"""
from pymongo import MongoClient

from .config import settings

# MongoClient does not connect until the first operation, so this is import-safe.
client = MongoClient(settings.mongo_uri)
db = client["ecommerce_db"]

products_collection = db["products"]
