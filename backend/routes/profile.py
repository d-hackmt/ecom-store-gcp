"""
Account management endpoints: view/edit profile, avatar upload, account deletion.
Registration/login live in auth.py.
"""
import logfire
from fastapi import APIRouter, HTTPException, UploadFile, File, Form

from ..database import users_collection, cart_collection
from ..models import ProfileUpdate, AccountDelete
from ..utils.images import encode_upload_to_base64, to_data_url
from ..utils.mongo import case_insensitive_exact
from ..utils.passwords import hash_password, verify_password
from ..utils.users import public_user

# Split so the read replica / write replica of the deployment can each mount only
# the half it serves. The monolith (main.py) mounts both.
read_router = APIRouter(prefix="/auth", tags=["Auth"])
write_router = APIRouter(prefix="/auth", tags=["Auth"])


@read_router.get("/profile")
def get_profile(email: str = ""):
    """Fetch a user's public profile (username, email, avatar)."""
    user = users_collection.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return public_user(user)


@write_router.put("/profile")
def update_profile(payload: ProfileUpdate):
    """
    Edit username/email/password. The current password must be supplied and
    correct to authorize any change, regardless of which fields are being edited.
    """
    current_email = payload.current_email.strip().lower()
    user = users_collection.find_one({"email": current_email})
    if not user:
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    if not user.get("password_hash"):
        raise HTTPException(
            status_code=400,
            detail="This account uses Google Sign-In and has no password to change here.",
        )
    if not verify_password(payload.current_password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    update_fields = {}

    if payload.new_username:
        new_username = payload.new_username.strip()
        if new_username.lower() != user["username"].lower():
            existing = users_collection.find_one({"username": case_insensitive_exact(new_username)})
            if existing and existing["_id"] != user["_id"]:
                raise HTTPException(status_code=400, detail="That username is already taken")
        update_fields["username"] = new_username

    if payload.new_email:
        new_email = payload.new_email.strip().lower()
        if new_email != current_email:
            existing = users_collection.find_one({"email": new_email})
            if existing and existing["_id"] != user["_id"]:
                raise HTTPException(status_code=400, detail="An account with that email already exists")
        update_fields["email"] = new_email

    if payload.new_password:
        if len(payload.new_password) < 6:
            raise HTTPException(status_code=400, detail="New password must be at least 6 characters")
        if len(payload.new_password.encode("utf-8")) > 72:
            raise HTTPException(status_code=400, detail="New password must be at most 72 bytes")
        update_fields["password_hash"] = hash_password(payload.new_password)

    if not update_fields:
        raise HTTPException(status_code=400, detail="Nothing to update")

    users_collection.update_one({"_id": user["_id"]}, {"$set": update_fields})
    updated_user = users_collection.find_one({"_id": user["_id"]})
    return {"message": "Profile updated successfully", **public_user(updated_user)}


@write_router.post("/avatar")
async def upload_avatar(email: str = Form(...), avatar: UploadFile = File(...)):
    """Upload/replace a user's profile picture, stored as base64 in MongoDB."""
    user = users_collection.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    base64_image, content_type = await encode_upload_to_base64(avatar)

    users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"avatar_data": base64_image, "avatar_content_type": content_type}},
    )
    return {"message": "Avatar updated", "avatar": to_data_url(base64_image, content_type)}


@write_router.delete("/account")
def delete_account(payload: AccountDelete):
    """Permanently delete an account (and its cart) after verifying the password."""
    email = payload.email.strip().lower()
    user = users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect password")
    if not user.get("password_hash"):
        raise HTTPException(
            status_code=400,
            detail="This account uses Google Sign-In; contact support to delete it.",
        )
    if not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect password")

    users_collection.delete_one({"_id": user["_id"]})
    cart_collection.delete_many({"user_email": email})
    logfire.info("Account deleted: {email}", email=email)
    return {"message": "Account deleted successfully"}
