"""
Centralised configuration.

Every environment variable the app reads is declared here once as a typed field
on :class:`Settings`, and ``.env`` is loaded in exactly one place — this module.
Import the singleton anywhere:

    from backend.config import settings
    MongoClient(settings.mongo_uri)
"""
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Populate os.environ from .env once, for libraries that read it directly.
load_dotenv()


class Settings(BaseSettings):
    """Typed view of the process environment (and ``.env``)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Database ---
    mongo_uri: str | None = None

    # --- Google Sign-In (public client id, not a secret) ---
    google_client_id: str = ""


settings = Settings()
