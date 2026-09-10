"""
Chatbot API - Text2NoSQL shopping assistant using Pydantic AI.

How it works:
- Every incoming message is screened by two Groq guardrail models first (see
  backend/chatbot/guardrails.py) — the input guard. Flagged messages never
  reach the agent.
- Normal conversation (greetings, questions): agent replies with plain text.
- Product queries (show me X, find Y under Z price): agent calls `search_products`
  (see backend/chatbot/agent.py) which queries MongoDB and returns matches.
- Before the agent's reply is sent back, it's screened again — the output
  guard — so a reply that slipped past the input guard (prompt leaks, made-up
  promises, unsafe content) still gets caught before it reaches the user.
- This endpoint figures out which type of response to send to the frontend.
"""
import asyncio

import logfire
from fastapi import APIRouter, Body

from ..config import SUPPORT_PHONE
from ..chatbot.agent import agent, StoreDeps
from ..chatbot.guardrails import (
    GUARDRAIL_BLOCKED_MESSAGE,
    is_prompt_injection,
    violates_content_policy,
    violates_output_policy,
)

# Split so the read replica / write replica of the deployment can each mount only
# the half it serves. The monolith (main.py) mounts both.
read_router = APIRouter(prefix="/chat", tags=["Chatbot"])
write_router = APIRouter(prefix="/chat", tags=["Chatbot"])


@read_router.post("")
async def chat_bot(data: dict = Body(...)):
    """
    Main chat endpoint. Accepts a user message and returns either
    a plain text reply or a list of matching products.
    """
    user_message = data.get("message", "").strip()
    if not user_message:
        return {"type": "text", "message": "Please type a message!", "data": None}

    # Guardrails: screen the message with Groq's dedicated safety models before
    # it ever reaches the shopping agent. Fails open (logs + continues) if a
    # guardrail call itself errors, so a Groq hiccup doesn't take down chat.
    try:
        is_injection, is_unsafe = await asyncio.gather(
            is_prompt_injection(user_message),
            violates_content_policy(user_message),
        )
        if is_injection or is_unsafe:
            return {"type": "text", "message": GUARDRAIL_BLOCKED_MESSAGE, "data": None}
    except Exception:
        logfire.exception("Guardrail check failed; failing open")

    deps = StoreDeps()

    try:
        result = await agent.run(user_message, deps=deps)
        text_reply = result.output  # plain string from the LLM

        # Output guard: screen the agent's reply before it reaches the user.
        # Fails open (logs + continues) if the guardrail call itself errors.
        try:
            if await violates_output_policy(text_reply):
                return {"type": "text", "message": GUARDRAIL_BLOCKED_MESSAGE, "data": None}
        except Exception:
            logfire.exception("Output guardrail check failed; failing open")

        if deps.found_products:
            return {
                "type": "products",
                "message": text_reply,
                "data": deps.found_products,
            }

        return {
            "type": "text",
            "message": text_reply,
            "data": None,
        }

    except Exception:
        logfire.exception("Chat agent run failed")
        return {
            "type": "text",
            "message": f"Sorry, I ran into an issue. Please try again or contact customer care at {SUPPORT_PHONE}.",
            "data": None,
        }
