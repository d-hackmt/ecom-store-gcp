"""
Admin gating based on an `is_admin` flag stored on the user's MongoDB
document — never in .env, since that's app/account data, not deployment config.

This app has no session tokens — "identity" is just a client-supplied email
(see state.sessionId on the frontend), sent via the X-User-Email header. This
check trusts that header, so it's an authorization/UX gate consistent with the
rest of the app, not a defense against a client that lies about its email.
"""
from fastapi import Header, HTTPException
from .database import users_collection


def is_admin(email: str | None) -> bool:
    if not email:
        return False
    user = users_collection.find_one({"email": email.strip().lower()})
    return bool(user and user.get("is_admin"))


def require_admin(x_user_email: str | None = Header(default=None)) -> str:
    """FastAPI dependency that guards admin-only routes."""
    if not is_admin(x_user_email):
        raise HTTPException(status_code=403, detail="Admin access required")
    return x_user_email
