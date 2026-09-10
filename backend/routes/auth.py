"""
Core identity endpoints: admin status check, and email/password registration
& login. Google Sign-In lives in google_auth.py; account editing
(profile/avatar/delete) lives in profile.py. Accounts (username, email,
hashed password) are stored in MongoDB, never in .env.
"""
from fastapi import APIRouter, HTTPException
from pymongo.errors import DuplicateKeyError

from ..auth import is_admin
from ..database import users_collection
from ..models import UserRegister, UserLogin
from ..utils.mongo import case_insensitive_exact
from ..utils.passwords import hash_password, verify_password
from ..utils.users import public_user

# Split so the read replica / write replica of the deployment can each mount only
# the half it serves. The monolith (main.py) mounts both.
read_router = APIRouter(prefix="/auth", tags=["Auth"])
write_router = APIRouter(prefix="/auth", tags=["Auth"])


@read_router.get("/is-admin")
def check_is_admin(email: str = ""):
    """Check whether the given email is a configured admin."""
    return {"is_admin": is_admin(email)}


@write_router.post("/register")
def register(user: UserRegister):
    """Register a new account with a username, email, and password."""
    username = user.username.strip()
    email = user.email.strip().lower()
    password = user.password

    if not username or not email or not password:
        raise HTTPException(status_code=400, detail="Username, email, and password are all required")
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    if len(password.encode("utf-8")) > 72:
        raise HTTPException(status_code=400, detail="Password must be at most 72 bytes")

    if users_collection.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="An account with that email already exists")
    if users_collection.find_one({"username": case_insensitive_exact(username)}):
        raise HTTPException(status_code=400, detail="That username is already taken")

    new_user = {
        "username": username,
        "email": email,
        "password_hash": hash_password(password),
    }
    try:
        users_collection.insert_one(new_user)
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="That email or username is already registered")

    return {"message": "Account created successfully", **public_user(new_user)}


@write_router.post("/login")
def login(credentials: UserLogin):
    """Log in with an email or username, plus password."""
    identifier = credentials.identifier.strip()
    user = users_collection.find_one({
        "$or": [
            {"email": identifier.lower()},
            {"username": case_insensitive_exact(identifier)},
        ]
    })
    if not user or not verify_password(credentials.password, user.get("password_hash")):
        raise HTTPException(status_code=401, detail="Invalid email/username or password")

    return {"message": "Login successful", **public_user(user)}
