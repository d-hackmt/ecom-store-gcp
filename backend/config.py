"""
Centralised configuration.

Every environment variable the app reads is declared here once as a typed field
on :class:`Settings`, and ``.env`` is loaded in exactly one place — this module.
Import the singleton anywhere:

    from backend.config import settings
    MongoClient(settings.mongo_uri)

Modules that hand raw environment values straight to a third-party client (for
example ``groq.AsyncGroq()``, which reads ``GROQ_API_KEY`` itself) keep working:
importing this module also runs ``load_dotenv()``, which populates ``os.environ``.
"""
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Populate os.environ from .env once, for libraries that read it directly.
load_dotenv()

# Customer-care number the chatbot and guardrail refusals point users to.
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

    # --- Database ---
    mongo_uri: str | None = None

    # --- LLM provider ---
    groq_api_key: str | None = None

    # --- Portkey LLM gateway (optional; falls back to calling Groq directly) ---
    portkey_api_key: str = ""
    portkey_groq_provider: str = "groq"

    # --- Model ids (overridable without a code change) ---
    # gpt-oss-20b is a Groq *production*-tier model (the guard models below are
    # only available as preview, but they are purpose-built and have no
    # production equivalent). Groq's offline eval judge stays on gpt-oss-120b.
    agent_model_name: str = "openai/gpt-oss-20b"          # the shopping agent's LLM
    guard_model_name: str = "openai/gpt-oss-safeguard-20b"
    prompt_guard_model_name: str = "meta-llama/llama-prompt-guard-2-86m"

    # --- Google Sign-In (public client id, not a secret) ---
    google_client_id: str = ""

    # --- Observability ---
    # This project historically stored the Logfire token as LOGFIRE_API_KEY; the
    # SDK itself looks for LOGFIRE_TOKEN. Accept either, preferring the SDK name.
    logfire_token: str | None = None
    logfire_api_key: str | None = None

    # Attach the live pydantic-evals evaluators to the agent (see
    # backend/chatbot/online_evals.py) so every real chat gets scored in the
    # background. Off by default — evals here run offline only, via
    # `python -m backend.evals.chatbot_evals`. Set ONLINE_EVALS_ENABLED=true to
    # turn this back on.
    online_evals_enabled: bool = False

    @property
    def logfire_write_token(self) -> str | None:
        return self.logfire_token or self.logfire_api_key


settings = Settings()
