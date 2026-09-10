"""
Google Sign-In: token verification and auto-registration. Split out from
auth.py since it's a distinct identity mechanism (no password involved —
Google's signature on the ID token is the proof of identity).
"""
import re

from fastapi import APIRouter, HTTPException
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token

from ..config import settings
from ..database import users_collection
from ..models import GoogleAuth
from ..utils.mongo import case_insensitive_exact
from ..utils.users import public_user

# Split so the read replica / write replica of the deployment can each mount only
# the half it serves. The monolith (main.py) mounts both.
read_router = APIRouter(prefix="/auth", tags=["Auth"])
write_router = APIRouter(prefix="/auth", tags=["Auth"])

GOOGLE_CLIENT_ID = settings.google_client_id


@read_router.get("/google-client-id")
def get_google_client_id():
    """Expose the Google OAuth Client ID to the frontend (public, not a secret)."""
    return {"client_id": GOOGLE_CLIENT_ID}


def _unique_username_from(base: str) -> str:
    """Turn a Google display name (or email prefix) into a free username."""
    base = re.sub(r"[^A-Za-z0-9_]", "", base) or "user"
    candidate = base
    suffix = 1
    while users_collection.find_one({"username": case_insensitive_exact(candidate)}):
        suffix += 1
        candidate = f"{base}{suffix}"
    return candidate


@write_router.post("/google")
def google_login(payload: GoogleAuth):
    """
    Verify a Google Identity Services ID token and log in — auto-registering
    the account if this is a new email. No password is required or checked;
    Google's signature on the token is the proof of identity.
    """
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=503, detail="Google Sign-In is not configured on this server")

    try:
        idinfo = google_id_token.verify_oauth2_token(
            payload.credential, google_requests.Request(), GOOGLE_CLIENT_ID
        )
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google credential")

    if not idinfo.get("email_verified"):
        raise HTTPException(status_code=401, detail="Google account email is not verified")

    email = (idinfo.get("email") or "").strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Google account has no email")

    user = users_collection.find_one({"email": email})
    if user is None:
        username = _unique_username_from(idinfo.get("name") or email.split("@")[0])
        user = {
            "username": username,
            "email": email,
            "password_hash": None,
            "auth_provider": "google",
        }
        users_collection.insert_one(user)

    return {"message": "Login successful", **public_user(user)}
