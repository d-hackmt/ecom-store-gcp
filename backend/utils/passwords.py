"""
Password hashing, via bcrypt directly (not passlib — its bcrypt backend is
broken against bcrypt >=4.1, an unfixed upstream bug in the unmaintained
passlib project).
"""
import bcrypt


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str | None) -> bool:
    """False (not a crash) for accounts with no password set — e.g. Google-only sign-ins."""
    if not password_hash:
        return False
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
