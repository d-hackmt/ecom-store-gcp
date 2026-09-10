# LUXE Shopping Assistant — POC

A standalone proof of concept: a chatbot that answers natural-language questions
about the LUXE product catalog ("men's shirts under ₹2000") by turning them into
MongoDB queries, wrapped in safety guardrails.

> **Branch 2 of 3.** This is the assistant on its own — no storefront, no cart,
> no accounts. It's the "prove it's possible" stage of a Forward-Deployed-AI
> story. See the [`main`](../../tree/main) branch for the full picture
> (`docs/STORY.md` there) and [`01-store-only`](../../tree/01-store-only) for the
> client's existing store.

## What's here

| | |
|---|---|
| **`app/chatbot/`** | The portable assistant: `agent.py` (Pydantic AI agent + `search_products` tool), `guardrails.py` (two Groq safety models), `pipeline.py` (`run_chat()` — the whole flow). This package drops into the real backend at integration time, unchanged. |
| **`app/api.py`** | One endpoint, `POST /chat`, calling `run_chat` — the same function the real store's route calls. |
| **`app/config.py` · `app/database.py`** | Slim: LLM keys + a read-only handle on the client's product collection. |
| **`web/`** | A minimal one-page chat UI. |

## Quick start

```bash
cp .env.example .env          # fill in MONGO_URI and GROQ_API_KEY
uv venv clothenv && source clothenv/Scripts/activate
uv pip install -r requirements.txt
python main.py                # http://localhost:8000
```

## Tests

```bash
uv pip install -r requirements-dev.txt
pytest
```

Fully offline — the product collection is an in-memory fake and the LLM boundary
is mocked.

## Docs

- [`docs/README.md`](docs/README.md) — how the POC works
- [`docs/client-schema.md`](docs/client-schema.md) — the product schema the client shared
