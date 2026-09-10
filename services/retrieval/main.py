"""
Retrieval service — every read-only endpoint: product listing/detail,
admin/profile lookups, cart/order history, and the AI shopping assistant (the
chatbot only ever queries MongoDB, never writes). Also serves the frontend,
since browsing is read-heavy.

It mounts the `read_router` of each shared route module (see backend/routes/).
Nothing is duplicated or reimplemented — the same route functions back the
monolith (main.py) and the ingestion service. There is no data split, only an
API split; all three share backend/ and the same MongoDB Atlas cluster.
"""
from contextlib import asynccontextmanager

import logfire
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.routes import products, orders, cart, chatbot, auth, google_auth, profile
from backend.config import settings
from backend.database import ensure_indexes

READ_MODULES = (products, orders, cart, chatbot, auth, google_auth, profile)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run once on startup: create the unique-account indexes in MongoDB."""
    ensure_indexes()
    yield


app = FastAPI(title="ClothStore Retrieval Service", lifespan=lifespan)

logfire.configure(send_to_logfire="if-token-present", token=settings.logfire_write_token)
logfire.instrument_fastapi(app)
logfire.instrument_pydantic()

# The frontend served here calls out to the ingestion service (a different
# origin once split across containers/ports) for every write.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

for module in READ_MODULES:
    app.include_router(module.read_router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "retrieval"}


@app.get("/config")
def frontend_config():
    """
    Tells the frontend where the ingestion service actually lives. Set via
    INGESTION_SERVICE_URL at deploy time (e.g. its Cloud Run URL) — the two
    services get unrelated hostnames on Cloud Run, so the frontend can't
    guess this the way it can for a same-host docker-compose setup.
    """
    return {"ingestion_base_url": settings.ingestion_service_url}


# Serve the vanilla-JS frontend at the root.
app.mount("/", StaticFiles(directory="Frontend", html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    print("Starting Retrieval Service...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
