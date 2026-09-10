"""
Centralised configuration.

Every environment variable the app reads is declared here once as a typed field
on :class:`Settings`, and ``.env`` is loaded in exactly one place — this module.
Import the singleton anywhere:

    from app.config import settings
    MongoClient(settings.mongo_uri)

Modules that hand raw environment values straight to a third-party client (for
example ``groq.AsyncGroq()``, which reads ``GROQ_API_KEY`` itself) keep working:
importing this module also runs ``load_dotenv()``, which populates ``os.environ``.
"""
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Populate os.environ from .env once, for libraries that read it directly.
load_dotenv()

# Customer-care number the assistant and guardrail refusals point users to.
SUPPORT_PHONE = "546464434"

# The single canonical refusal sentence — used by the guardrails, the agent's
# system prompt, and anywhere else the assistant declines a request.
REFUSAL_MESSAGE = (
    f"Sorry, I can't help with that. For assistance, contact our customer care at {SUPPORT_PHONE}."
)


def is_placeholder(value: str | None) -> bool:
    """True for an unset value or an untouched ``.env.example`` placeholder."""
    return not value or value.strip().upper().startswith("REPLACE_WITH")


class Settings(BaseSettings):
    """Typed view of the process environment (and ``.env``)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Database (the client's product catalog — read only) ---
    mongo_uri: str | None = None

    # --- LLM provider ---
    groq_api_key: str | None = None

    # --- Portkey LLM gateway (optional; falls back to calling Groq directly) ---
    portkey_api_key: str = ""
    portkey_groq_provider: str = "groq"

    # --- Model ids (overridable without a code change) ---
    # gpt-oss-20b is a Groq *production*-tier model; the guard models are
    # purpose-built (preview tier) and have no production equivalent.
    agent_model_name: str = "openai/gpt-oss-20b"
    guard_model_name: str = "openai/gpt-oss-safeguard-20b"
    prompt_guard_model_name: str = "meta-llama/llama-prompt-guard-2-86m"

    # Live pydantic-evals evaluators. Off in this POC — that's what the
    # integration on the `main` branch adds. `agent.py` reads this and is
    # otherwise byte-for-byte identical between here and `main`.
    online_evals_enabled: bool = False


settings = Settings()
