"""
POST /chat — the shopping-assistant endpoint.

All the orchestration (input guards -> agent -> output guard -> response shaping)
lives in backend/chatbot/pipeline.py, so the exact same pipeline backs the
standalone chatbot POC. This module is only the HTTP layer.
"""
from fastapi import APIRouter, Body

from ..chatbot.pipeline import run_chat

# Split so the read replica / write replica of the deployment can each mount only
# the half it serves. The monolith (main.py) mounts both. The chatbot only reads
# from MongoDB, so it lives on the read side; write_router stays empty.
read_router = APIRouter(prefix="/chat", tags=["Chatbot"])
write_router = APIRouter(prefix="/chat", tags=["Chatbot"])


@read_router.post("")
async def chat_bot(data: dict = Body(...)):
    """
    Accept ``{"message": "..."}`` and return either a plain-text reply or a list
    of matching products: ``{"type": "text" | "products", "message", "data"}``.
    """
    return await run_chat(data.get("message", ""))
