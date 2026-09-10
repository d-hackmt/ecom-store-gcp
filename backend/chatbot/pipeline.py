"""
The chat pipeline — the full journey from a raw user message to the payload the
frontend renders:

    message
      -> input guards   (prompt-injection + content policy, run together)
      -> shopping agent  (which may call the search_products tool)
      -> output guard    (content policy on the agent's reply)
      -> {"type": "text" | "products", "message": str, "data": list | None}

Guardrail calls fail open: if a Groq call errors it is logged and the request
continues, so a safety-model hiccup never takes chat down. If the agent itself
errors, the user gets a friendly fallback pointing at customer care.

`run_chat` returns a plain dict and never raises, so the same pipeline backs both
the monolith's ``POST /chat`` route and the standalone chatbot POC.
"""
import asyncio

import logfire

from ..config import SUPPORT_PHONE
from .agent import agent, StoreDeps
from .guardrails import (
    GUARDRAIL_BLOCKED_MESSAGE,
    is_prompt_injection,
    violates_content_policy,
    violates_output_policy,
)

_EMPTY_MESSAGE_REPLY = {"type": "text", "message": "Please type a message!", "data": None}


def _blocked() -> dict:
    return {"type": "text", "message": GUARDRAIL_BLOCKED_MESSAGE, "data": None}


async def run_chat(message: str) -> dict:
    """
    Run one user message through the guardrails and the shopping agent.

    Always returns ``{"type", "message", "data"}`` — never raises.
    """
    user_message = (message or "").strip()
    if not user_message:
        return _EMPTY_MESSAGE_REPLY

    # Input guards: screen the message with Groq's safety models before the agent
    # ever sees it. Fails open (logs + continues) if a guardrail call itself errors.
    try:
        is_injection, is_unsafe = await asyncio.gather(
            is_prompt_injection(user_message),
            violates_content_policy(user_message),
        )
        if is_injection or is_unsafe:
            return _blocked()
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
                return _blocked()
        except Exception:
            logfire.exception("Output guardrail check failed; failing open")

        if deps.found_products:
            return {"type": "products", "message": text_reply, "data": deps.found_products}
        return {"type": "text", "message": text_reply, "data": None}

    except Exception:
        logfire.exception("Chat agent run failed")
        return {
            "type": "text",
            "message": (
                f"Sorry, I ran into an issue. Please try again or contact "
                f"customer care at {SUPPORT_PHONE}."
            ),
            "data": None,
        }
