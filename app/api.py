"""
The POC's HTTP layer: one endpoint plus a static demo page.

`POST /chat` hands the message straight to `run_chat` — the same pipeline
function that backs the real store's `POST /chat` route on the `main` branch.
That is the point of this POC: the chat code here is the code that ships.
"""
from fastapi import FastAPI, Body
from fastapi.staticfiles import StaticFiles

from .chatbot.pipeline import run_chat

app = FastAPI(title="LUXE Shopping Assistant — POC")


@app.post("/chat")
async def chat(data: dict = Body(...)):
    """
    Accept ``{"message": "..."}`` and return either a plain-text reply or a list
    of matching products: ``{"type": "text" | "products", "message", "data"}``.
    """
    return await run_chat(data.get("message", ""))


# The minimal demo page.
app.mount("/", StaticFiles(directory="web", html=True), name="web")
