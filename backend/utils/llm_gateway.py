"""
Optional LLM gateway routing via Portkey (https://portkey.ai — free Developer
tier: 10,000 logs/month, no card required; requests beyond that cap still go
through, you just stop getting logged).

When PORTKEY_API_KEY is set in .env, Groq calls (guardrails + the shopping
agent) are routed through Portkey's OpenAI-compatible gateway for
observability/reliability. Falls back to calling Groq directly when it isn't
configured, so the app works either way — see is_portkey_configured().

Setup: sign up at portkey.ai, add Groq as a provider in the Model Catalog
(pasting in your real GROQ_API_KEY there), then put your Portkey API key in
.env. PORTKEY_GROQ_PROVIDER should match whatever slug you gave that provider
in the dashboard (defaults to "groq").
"""
from ..config import is_placeholder, settings

PORTKEY_API_KEY = settings.portkey_api_key
# Accept the slug with or without a leading "@" (the Portkey dashboard displays
# it as "@clothing", but the env var shouldn't have to match that exactly).
PORTKEY_GROQ_PROVIDER = settings.portkey_groq_provider.lstrip("@")
PORTKEY_BASE_URL = "https://api.portkey.ai/v1"


def is_portkey_configured() -> bool:
    """True when a real Portkey API key is set (not blank, not a placeholder)."""
    return not is_placeholder(PORTKEY_API_KEY)


def resolve_model_name(raw_model_name: str) -> str:
    """Prefix a bare Groq model name with Portkey's `@provider/model` syntax when gateway-routed."""
    if is_portkey_configured():
        return f"@{PORTKEY_GROQ_PROVIDER}/{raw_model_name}"
    return raw_model_name
