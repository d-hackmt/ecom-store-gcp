"""
The POC's HTTP layer: one endpoint plus a static demo page.

`POST /chat` hands the message straight to `run_chat` — the same pipeline
function that backs the real store's `POST /chat` route on the `main` branch.
That is the point of this POC: the chat code here is the code that ships.
"""
import logfire
from fastapi import FastAPI, Body
from fastapi.staticfiles import StaticFiles

from .chatbot.pipeline import run_chat

# No-op unless LOGFIRE_TOKEN is set; lets the POC show traces when a token is
# provided, without requiring one.
logfire.configure(send_to_logfire="if-token-present")
logfire.instrument_pydantic_ai()

app = FastAPI(title="LUXE Shopping Assistant — POC")

logfire.instrument_fastapi(app)


@app.post("/chat")
async def chat(data: dict = Body(...)):
    """
    Accept ``{"message": "..."}`` and return either a plain-text reply or a list
    of matching products: ``{"type": "text" | "products", "message", "data"}``.
    """
    return await run_chat(data.get("message", ""))


# The minimal demo page.
app.mount("/", StaticFiles(directory="web", html=True), name="web")
