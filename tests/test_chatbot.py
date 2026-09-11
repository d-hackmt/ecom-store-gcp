"""
Tests for the chatbot HTTP layer (POST /chat) and the search_products agent tool.
The pipeline orchestration itself is covered in tests/test_pipeline.py.
"""
from types import SimpleNamespace
from unittest.mock import AsyncMock

import backend.chatbot.pipeline as pipeline
from backend.chatbot.agent import search_products, StoreDeps


def test_chat_route_delegates_to_pipeline(client, monkeypatch):
    """The endpoint is a thin adapter: it hands the message to run_chat and
    returns whatever that returns, unchanged."""
    monkeypatch.setattr(pipeline, "is_prompt_injection", AsyncMock(return_value=False))
    monkeypatch.setattr(pipeline, "violates_content_policy", AsyncMock(return_value=False))
    monkeypatch.setattr(pipeline, "violates_output_policy", AsyncMock(return_value=False))
    monkeypatch.setattr(pipeline.agent, "run", AsyncMock(return_value=SimpleNamespace(output="Hi there!")))

    res = client.post("/chat", json={"message": "hello"})

    assert res.status_code == 200
    assert res.json() == {"type": "text", "message": "Hi there!", "data": None}


def test_search_products_tool_resolves_image_and_strips_raw_fields(fake_db):
    """
    Unit test for the search_products tool itself (not through the agent/LLM):
    confirms it points "image" at the product's image endpoint and never
    leaks the raw base64 fields, matching GET /products behaviour.
    """
    fake_db["products"].insert_one({
        "name": "Test Product",
        "category": "men",
        "price": 500,
        "image_data": "ZmFrZQ==",
        "image_content_type": "image/png",
    })

    deps = StoreDeps()
    ctx = SimpleNamespace(deps=deps)
    result = search_products(ctx, category="men")

    assert "Found 1" in result
    product_id = deps.found_products[0]["id"]
    assert deps.found_products[0]["image"] == f"/products/{product_id}/image"
    assert "image_data" not in deps.found_products[0]
    assert "image_content_type" not in deps.found_products[0]
