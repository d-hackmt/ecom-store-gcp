from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.routes import products, products_bulk, orders, cart, auth, google_auth, profile
from backend.database import ensure_indexes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run once on startup: create the unique-account indexes in MongoDB."""
    ensure_indexes()
    yield


app = FastAPI(lifespan=lifespan)

# The monolith serves every endpoint — both halves of each route module.
ROUTE_MODULES = (products, products_bulk, orders, cart, auth, google_auth, profile)
for module in ROUTE_MODULES:
    app.include_router(module.read_router)
    app.include_router(module.write_router)


@app.get("/config")
def frontend_config():
    """
    Tells the frontend where the ingestion service lives. The monolith serves
    both reads and writes itself, so ingestion is just this same origin —
    without this, the frontend falls back to guessing port 8001 (the split
    services' ingestion port), which isn't running here and breaks any write
    call (e.g. Google sign-in) with a fetch failure.
    """
    return {"ingestion_base_url": ""}


# Serve the vanilla-JS frontend at the root.
app.mount("/", StaticFiles(directory="Frontend", html=True), name="frontend")

if __name__ == "__main__":
    print("Starting backend server (FastAPI)...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
