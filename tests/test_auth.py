"""
Tests for registration/login (auth.py), profile management (profile.py),
and admin status checks.
"""
from unittest.mock import MagicMock


def test_register_success(client):
    res = client.post("/auth/register", json={"username": "aanand", "email": "a@example.com", "password": "secret123"})
    assert res.status_code == 200
    body = res.json()
    assert body["username"] == "aanand"
    assert body["email"] == "a@example.com"
    assert body["avatar"] is None


def test_register_duplicate_email(client):
    client.post("/auth/register", json={"username": "a", "email": "dup@example.com", "password": "secret123"})
    res = client.post("/auth/register", json={"username": "b", "email": "dup@example.com", "password": "secret123"})
    assert res.status_code == 400
    assert "already exists" in res.json()["detail"]


def test_register_duplicate_username_case_insensitive(client):
    client.post("/auth/register", json={"username": "JohnDoe", "email": "john1@example.com", "password": "secret123"})
    res = client.post("/auth/register", json={"username": "johndoe", "email": "john2@example.com", "password": "secret123"})
    assert res.status_code == 400
    assert "username" in res.json()["detail"].lower()


def test_register_short_password_rejected(client):
    res = client.post("/auth/register", json={"username": "x", "email": "x@example.com", "password": "123"})
    assert res.status_code == 400


def test_register_missing_fields_rejected(client):
    res = client.post("/auth/register", json={"username": "", "email": "x@example.com", "password": "secret123"})
    assert res.status_code == 400


def test_login_with_email(client):
    client.post("/auth/register", json={"username": "loginuser", "email": "login@example.com", "password": "secret123"})
    res = client.post("/auth/login", json={"identifier": "login@example.com", "password": "secret123"})
    assert res.status_code == 200
    assert res.json()["username"] == "loginuser"


def test_login_with_username(client):
    client.post("/auth/register", json={"username": "loginuser2", "email": "login2@example.com", "password": "secret123"})
    res = client.post("/auth/login", json={"identifier": "loginuser2", "password": "secret123"})
    assert res.status_code == 200
    assert res.json()["email"] == "login2@example.com"


def test_login_wrong_password(client):
    client.post("/auth/register", json={"username": "u", "email": "wp@example.com", "password": "secret123"})
    res = client.post("/auth/login", json={"identifier": "wp@example.com", "password": "wrongpass"})
    assert res.status_code == 401


def test_login_unknown_user(client):
    res = client.post("/auth/login", json={"identifier": "nobody@example.com", "password": "whatever"})
    assert res.status_code == 401


def test_is_admin_false_for_regular_user(client):
    client.post("/auth/register", json={"username": "reg", "email": "reg@example.com", "password": "secret123"})
    res = client.get("/auth/is-admin", params={"email": "reg@example.com"})
    assert res.json() == {"is_admin": False}


def test_is_admin_true_for_flagged_user(client, admin_user):
    res = client.get("/auth/is-admin", params={"email": admin_user["email"]})
    assert res.json() == {"is_admin": True}


def test_is_admin_false_for_unknown_email(client):
    res = client.get("/auth/is-admin", params={"email": "nobody@example.com"})
    assert res.json() == {"is_admin": False}


# --- Profile management ---

def test_get_profile(client):
    client.post("/auth/register", json={"username": "prof", "email": "prof@example.com", "password": "secret123"})
    res = client.get("/auth/profile", params={"email": "prof@example.com"})
    assert res.status_code == 200
    assert res.json() == {"username": "prof", "email": "prof@example.com", "avatar": None}


def test_get_profile_not_found(client):
    res = client.get("/auth/profile", params={"email": "nobody@example.com"})
    assert res.status_code == 404


def test_update_profile_wrong_current_password(client):
    client.post("/auth/register", json={"username": "edit1", "email": "edit1@example.com", "password": "secret123"})
    res = client.put("/auth/profile", json={
        "current_email": "edit1@example.com",
        "current_password": "wrongpass",
        "new_username": "newname",
    })
    assert res.status_code == 401


def test_update_profile_username_and_password(client):
    client.post("/auth/register", json={"username": "edit2", "email": "edit2@example.com", "password": "secret123"})
    res = client.put("/auth/profile", json={
        "current_email": "edit2@example.com",
        "current_password": "secret123",
        "new_username": "edited",
        "new_password": "newpass456",
    })
    assert res.status_code == 200
    assert res.json()["username"] == "edited"

    # Old password should no longer work; new one should.
    assert client.post("/auth/login", json={"identifier": "edit2@example.com", "password": "secret123"}).status_code == 401
    assert client.post("/auth/login", json={"identifier": "edit2@example.com", "password": "newpass456"}).status_code == 200


def test_update_profile_nothing_to_update(client):
    client.post("/auth/register", json={"username": "edit3", "email": "edit3@example.com", "password": "secret123"})
    res = client.put("/auth/profile", json={"current_email": "edit3@example.com", "current_password": "secret123"})
    assert res.status_code == 400


def test_update_profile_rejects_passwordless_google_account(client, fake_db):
    fake_db["users"].insert_one(
        {"username": "goog", "email": "goog@gmail.com", "password_hash": None, "auth_provider": "google"}
    )
    res = client.put("/auth/profile", json={
        "current_email": "goog@gmail.com",
        "current_password": "anything",
        "new_username": "goog2",
    })
    assert res.status_code == 400
    assert "Google" in res.json()["detail"]


def test_upload_avatar(client):
    client.post("/auth/register", json={"username": "avataruser", "email": "avatar@example.com", "password": "secret123"})
    res = client.post(
        "/auth/avatar",
        data={"email": "avatar@example.com"},
        files={"avatar": ("pic.jpg", b"fakejpegbytes", "image/jpeg")},
    )
    assert res.status_code == 200
    assert res.json()["avatar"].startswith("data:image/jpeg;base64,")

    profile = client.get("/auth/profile", params={"email": "avatar@example.com"}).json()
    assert profile["avatar"].startswith("data:image/jpeg;base64,")


def test_delete_account_wrong_password(client):
    client.post("/auth/register", json={"username": "del1", "email": "del1@example.com", "password": "secret123"})
    res = client.request("DELETE", "/auth/account", json={"email": "del1@example.com", "password": "wrongpass"})
    assert res.status_code == 401


def test_delete_account_rejects_passwordless_google_account(client, fake_db):
    fake_db["users"].insert_one(
        {"username": "goog2", "email": "goog2@gmail.com", "password_hash": None, "auth_provider": "google"}
    )
    res = client.request("DELETE", "/auth/account", json={"email": "goog2@gmail.com", "password": "anything"})
    assert res.status_code == 400
    assert "Google" in res.json()["detail"]


def test_delete_account_success_removes_user_and_cart(client, fake_db):
    client.post("/auth/register", json={"username": "del2", "email": "del2@example.com", "password": "secret123"})
    client.post("/cart/add", json={"user_email": "del2@example.com", "product_name": "Shirt", "quantity": 1})

    res = client.request("DELETE", "/auth/account", json={"email": "del2@example.com", "password": "secret123"})
    assert res.status_code == 200

    assert client.get("/auth/profile", params={"email": "del2@example.com"}).status_code == 404
    assert client.get("/cart/del2@example.com").json() == []


# --- Google Sign-In ---

def test_google_login_not_configured(client, monkeypatch):
    import backend.routes.google_auth as auth_routes
    monkeypatch.setattr(auth_routes, "GOOGLE_CLIENT_ID", "")
    res = client.post("/auth/google", json={"credential": "whatever"})
    assert res.status_code == 503


def test_google_login_new_user_auto_registers(client, monkeypatch):
    import backend.routes.google_auth as auth_routes
    monkeypatch.setattr(auth_routes, "GOOGLE_CLIENT_ID", "fake-client-id")
    monkeypatch.setattr(
        auth_routes.google_id_token,
        "verify_oauth2_token",
        MagicMock(return_value={"email": "new@gmail.com", "email_verified": True, "name": "New User"}),
    )
    res = client.post("/auth/google", json={"credential": "fake-token"})
    assert res.status_code == 200
    body = res.json()
    assert body["email"] == "new@gmail.com"
    assert body["username"] == "NewUser"


def test_google_login_existing_email_no_duplicate(client, monkeypatch, fake_db):
    import backend.routes.google_auth as auth_routes
    monkeypatch.setattr(auth_routes, "GOOGLE_CLIENT_ID", "fake-client-id")
    monkeypatch.setattr(
        auth_routes.google_id_token,
        "verify_oauth2_token",
        MagicMock(return_value={"email": "repeat@gmail.com", "email_verified": True, "name": "Repeat User"}),
    )
    client.post("/auth/google", json={"credential": "fake-token"})
    client.post("/auth/google", json={"credential": "fake-token"})
    assert fake_db["users"].count_documents({"email": "repeat@gmail.com"}) == 1


def test_google_login_unverified_email_rejected(client, monkeypatch):
    import backend.routes.google_auth as auth_routes
    monkeypatch.setattr(auth_routes, "GOOGLE_CLIENT_ID", "fake-client-id")
    monkeypatch.setattr(
        auth_routes.google_id_token,
        "verify_oauth2_token",
        MagicMock(return_value={"email": "unverified@gmail.com", "email_verified": False}),
    )
    res = client.post("/auth/google", json={"credential": "fake-token"})
    assert res.status_code == 401


def test_google_login_invalid_token_rejected(client, monkeypatch):
    import backend.routes.google_auth as auth_routes
    monkeypatch.setattr(auth_routes, "GOOGLE_CLIENT_ID", "fake-client-id")

    def raise_value_error(*args, **kwargs):
        raise ValueError("bad token")

    monkeypatch.setattr(auth_routes.google_id_token, "verify_oauth2_token", raise_value_error)
    res = client.post("/auth/google", json={"credential": "garbage"})
    assert res.status_code == 401
