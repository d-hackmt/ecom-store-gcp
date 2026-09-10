import uvicorn

from app.api import app  # noqa: F401  (re-exported so `uvicorn main:app` works)

if __name__ == "__main__":
    print("Starting LUXE assistant POC (http://localhost:8000)...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
