"""
Shared pytest fixtures.

The suite never touches the real MongoDB Atlas cluster: every collection is
swapped for an in-memory fake. This keeps `pytest` fast, free, and safe to run
on every push (see githooks/pre-push).
"""
import re
import copy

import pytest
from bson import ObjectId
from fastapi.testclient import TestClient


class FakeCursor(list):
    """Just enough of a pymongo Cursor to support .sort()/.limit() chaining."""

    def sort(self, key, direction=1):
        return FakeCursor(sorted(self, key=lambda d: d.get(key), reverse=(direction == -1)))

    def limit(self, n):
        return FakeCursor(self[:n])


class DeleteResult:
    def __init__(self, deleted_count):
        self.deleted_count = deleted_count


class UpdateResult:
    def __init__(self, matched_count):
        self.matched_count = matched_count


class FakeCollection:
    """Minimal in-memory stand-in for a pymongo Collection."""

    def __init__(self):
        self.docs = []

    def _matches(self, doc, query):
        for key, value in query.items():
            if key == "$or":
                if not any(self._matches(doc, cond) for cond in value):
                    return False
            elif isinstance(value, dict) and "$regex" in value:
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
            else:
                if doc.get(key) != value:
                    return False
        return True

    def _project(self, doc, projection):
        if not projection:
            return copy.deepcopy(doc)
        result = copy.deepcopy(doc)
        for field, include in projection.items():
            if not include:
                result.pop(field, None)
        return result

    def find_one(self, query=None, projection=None):
        query = query or {}
        for doc in self.docs:
            if self._matches(doc, query):
                return self._project(doc, projection) if projection else doc
        return None

    def find(self, query=None, projection=None):
        query = query or {}
        results = [self._project(d, projection) for d in self.docs if self._matches(d, query)]
        return FakeCursor(results)

    def insert_one(self, doc):
        # Real ObjectIds — not sequential ints — so code that does ObjectId(id)
        # to parse a URL param (as the real routes do) works against the fake too.
        if "_id" not in doc:
            doc["_id"] = ObjectId()
        self.docs.append(doc)
        return doc

    def insert_many(self, docs):
        for doc in docs:
            self.insert_one(doc)

    def update_one(self, query, update):
        doc = self.find_one(query)
        if doc:
            doc.update(update.get("$set", {}))
            for field, delta in update.get("$inc", {}).items():
                doc[field] = doc.get(field, 0) + delta
        return UpdateResult(matched_count=1 if doc else 0)

    def delete_one(self, query):
        doc = self.find_one(query)
        if doc:
            self.docs.remove(doc)
        return DeleteResult(deleted_count=1 if doc else 0)

    def delete_many(self, query=None):
        query = query or {}
        matched = [d for d in self.docs if self._matches(d, query)]
        for d in matched:
            self.docs.remove(d)
        return DeleteResult(deleted_count=len(matched))

    def count_documents(self, query=None):
        return len(self.find(query or {}))

    def create_index(self, *args, **kwargs):
        pass  # no-op — the fake has no real index enforcement


@pytest.fixture
def fake_db(monkeypatch):
    """Patch every module-level collection reference across the app with isolated fakes."""
    users = FakeCollection()
    products = FakeCollection()
    orders = FakeCollection()
    cart = FakeCollection()

    import backend.database as database
    monkeypatch.setattr(database, "users_collection", users)
    monkeypatch.setattr(database, "products_collection", products)
    monkeypatch.setattr(database, "orders_collection", orders)
    monkeypatch.setattr(database, "cart_collection", cart)

    # Each module imported its collection directly at import time
    # (`from ..database import x`), so the reference has to be patched there too.
    import backend.auth as auth_core
    import backend.routes.products as products_routes
    import backend.routes.products_bulk as products_bulk_routes
    import backend.routes.auth as auth_routes
    import backend.routes.google_auth as google_auth_routes
    import backend.routes.profile as profile_routes
    import backend.routes.orders as orders_routes
    import backend.routes.cart as cart_routes

    monkeypatch.setattr(auth_core, "users_collection", users)
    monkeypatch.setattr(products_routes, "products_collection", products)
    monkeypatch.setattr(products_bulk_routes, "products_collection", products)
    monkeypatch.setattr(auth_routes, "users_collection", users)
    monkeypatch.setattr(google_auth_routes, "users_collection", users)
    monkeypatch.setattr(profile_routes, "users_collection", users)
    monkeypatch.setattr(profile_routes, "cart_collection", cart)
    monkeypatch.setattr(orders_routes, "orders_collection", orders)
    monkeypatch.setattr(cart_routes, "cart_collection", cart)

    return {"users": users, "products": products, "orders": orders, "cart": cart}


@pytest.fixture
def client(fake_db):
    import main
    return TestClient(main.app)


@pytest.fixture
def admin_user(fake_db):
    """An admin account already sitting in the fake users collection."""
    user = {
        "username": "admin",
        "email": "admin@example.com",
        "password_hash": None,
        "is_admin": True,
    }
    fake_db["users"].insert_one(user)
    return user


@pytest.fixture
def admin_headers(admin_user):
    return {"X-User-Email": admin_user["email"]}
