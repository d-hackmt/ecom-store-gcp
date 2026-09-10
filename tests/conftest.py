"""
Shared pytest fixtures.

The suite never touches the real MongoDB Atlas cluster and never calls real
Groq/Portkey APIs: the product collection is an in-memory fake and the LLM
boundary is mocked. `pytest` stays fast, free, and safe to run on every push.
"""
import re
import copy

import pytest
from bson import ObjectId
from fastapi.testclient import TestClient


class FakeCursor(list):
    """Just enough of a pymongo Cursor to support .limit() chaining."""

    def limit(self, n):
        return FakeCursor(self[:n])


class FakeCollection:
    """Minimal in-memory stand-in for a pymongo Collection (read paths only)."""

    def __init__(self):
        self.docs = []

    def _matches(self, doc, query):
        for key, value in query.items():
            if isinstance(value, dict) and "$regex" in value:
                flags = re.IGNORECASE if value.get("$options") == "i" else 0
                if not re.match(value["$regex"], str(doc.get(key, "")), flags):
                    return False
            elif isinstance(value, dict) and ("$gte" in value or "$lte" in value):
                actual = doc.get(key)
                if actual is None:
                    return False
                if "$gte" in value and actual < value["$gte"]:
                    return False
                if "$lte" in value and actual > value["$lte"]:
                    return False
            elif doc.get(key) != value:
                return False
        return True

    def find(self, query=None):
        query = query or {}
        return FakeCursor(copy.deepcopy(d) for d in self.docs if self._matches(d, query))

    def insert_one(self, doc):
        doc.setdefault("_id", ObjectId())
        self.docs.append(doc)
        return doc


@pytest.fixture
def fake_products(monkeypatch):
    """Swap the module-level product collection for an isolated in-memory fake."""
    products = FakeCollection()

    import app.database as database
    import app.chatbot.agent as agent_module

    monkeypatch.setattr(database, "products_collection", products)
    monkeypatch.setattr(agent_module, "products_collection", products)
    return products


@pytest.fixture
def client(fake_products):
    from app.api import app
    return TestClient(app)
