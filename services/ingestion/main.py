"""
Ingestion service — every endpoint that writes to MongoDB: product
create/update/delete, bulk ingestion (JSON bulk, Excel+zip upload), account
registration/login/edits, cart writes, and order placement.

It mounts the `write_router` of each shared route module (see backend/routes/).
Nothing is duplicated or reimplemented — the same route functions back the
monolith (main.py) and the retrieval service. There is no data split, only an
API split; all three share backend/ and the same MongoDB Atlas cluster.
"""
from contextlib import asynccontextmanager

import logfire
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import products, products_bulk, orders, cart, auth, google_auth, profile
from backend.config import settings
from backend.database import ensure_indexes

# The chatbot is read-only and lives on the retrieval service, so it is not imported here.
WRITE_MODULES = (products, products_bulk, orders, cart, auth, google_auth, profile)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run once on startup: create the unique-account indexes in MongoDB."""
    ensure_indexes()
    yield


app = FastAPI(title="ClothStore Ingestion Service", lifespan=lifespan)

logfire.configure(send_to_logfire="if-token-present", token=settings.logfire_write_token)
logfire.instrument_fastapi(app)
logfire.instrument_pydantic()

# The frontend (served by the retrieval service, a different origin once split
# across containers/ports) calls straight into this service for writes.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

for module in WRITE_MODULES:
    app.include_router(module.write_router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "ingestion"}


if __name__ == "__main__":
    import uvicorn
    print("Starting Ingestion Service...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
