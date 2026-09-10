"""
Tests for the shopping cart (cart.py) and order placement/history (orders.py).
"""


def test_cart_add_and_get(client):
    res = client.post("/cart/add", json={"user_email": "a@example.com", "product_name": "Shirt", "quantity": 2})
    assert res.status_code == 200

    items = client.get("/cart/a@example.com").json()
    assert len(items) == 1
    assert items[0]["product_name"] == "Shirt"
    assert items[0]["quantity"] == 2
    assert "_id" not in items[0]


def test_cart_add_merges_quantity_for_same_product(client):
    client.post("/cart/add", json={"user_email": "a@example.com", "product_name": "Shirt", "quantity": 2})
    client.post("/cart/add", json={"user_email": "a@example.com", "product_name": "Shirt", "quantity": 3})

    items = client.get("/cart/a@example.com").json()
    assert len(items) == 1
    assert items[0]["quantity"] == 5


def test_cart_is_scoped_per_user(client):
    client.post("/cart/add", json={"user_email": "a@example.com", "product_name": "Shirt", "quantity": 1})
    client.post("/cart/add", json={"user_email": "b@example.com", "product_name": "Jeans", "quantity": 1})

    assert len(client.get("/cart/a@example.com").json()) == 1
    assert len(client.get("/cart/b@example.com").json()) == 1
    assert client.get("/cart/a@example.com").json()[0]["product_name"] == "Shirt"


def test_clear_cart(client):
    client.post("/cart/add", json={"user_email": "a@example.com", "product_name": "Shirt", "quantity": 1})
    res = client.delete("/cart/a@example.com")
    assert res.status_code == 200
    assert client.get("/cart/a@example.com").json() == []


def test_place_order_and_history(client):
    res = client.post("/orders", json={"user_email": "a@example.com", "product_name": "Shirt", "quantity": 2, "price": 499})
    assert res.status_code == 200

    history = client.get("/orders/a@example.com").json()
    assert len(history) == 1
    order = history[0]
    assert order["product_name"] == "Shirt"
    assert order["quantity"] == 2
    assert order["price"] == 499
    assert "created_at" in order
    assert "_id" not in order


def test_order_history_most_recent_first(client, fake_db):
    # Insert with explicit, distinct timestamps rather than two rapid real
    # POSTs — datetime.now() calls a few instructions apart can land on the
    # exact same microsecond on a fast machine, which would make this flaky.
    fake_db["orders"].insert_one({"user_email": "a@example.com", "product_name": "First", "quantity": 1, "price": 100, "created_at": "2026-01-01T00:00:00+00:00"})
    fake_db["orders"].insert_one({"user_email": "a@example.com", "product_name": "Second", "quantity": 1, "price": 200, "created_at": "2026-01-02T00:00:00+00:00"})

    history = client.get("/orders/a@example.com").json()
    assert [o["product_name"] for o in history] == ["Second", "First"]


def test_order_history_scoped_per_user(client):
    client.post("/orders", json={"user_email": "a@example.com", "product_name": "Shirt", "quantity": 1, "price": 100})
    client.post("/orders", json={"user_email": "b@example.com", "product_name": "Jeans", "quantity": 1, "price": 200})

    assert len(client.get("/orders/a@example.com").json()) == 1
    assert len(client.get("/orders/b@example.com").json()) == 1
