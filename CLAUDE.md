# CLAUDE.md — LUXE Shopping Assistant POC (`02-chatbot-poc`)

## What this branch is

A **standalone proof of concept** for a natural-language shopping assistant over
the LUXE product catalog. It is **branch 2 of 3**, a frozen snapshot in a
Forward-Deployed-AI-Engineer story. The `main` branch has the full picture
(`docs/STORY.md` there).

| Branch | Scope |
|--------|-------|
| `main` | Full integrated product: store + AI + guardrails + evals. Source of truth. |
| `01-store-only` | The plain store, no AI. Frozen. |
| `02-chatbot-poc` | **← this branch.** The assistant alone. Frozen. |

## Scope rule — assistant only

This branch is *just* the chatbot. **Do not** add a storefront, cart, orders,
accounts, admin, or write endpoints. It reads the product catalog and nothing
else.

`main` is the source of truth. This branch is derived and frozen; a change here
does not flow back. Keep `app/chatbot/` byte-for-byte identical to
`backend/chatbot/` on `main` (the only intended difference is
`settings.online_evals_enabled`, which is off here).

## Layout

```
app/
  config.py        slim Settings: MONGO_URI, GROQ_API_KEY, PORTKEY_*, model ids
  database.py      one read-only handle: products_collection
  chatbot/         the portable unit — drops into backend/chatbot/ at integration
    agent.py       Pydantic AI agent + search_products tool
    guardrails.py  two Groq safety-model checks
    pipeline.py    run_chat(message) -> dict  (guards -> agent -> guard -> shape)
  utils/           mongo query fragments, image data-URL helper, Portkey gateway
  api.py           FastAPI: POST /chat -> run_chat ; serves web/
web/               minimal one-page chat UI (index.html + app.js)
main.py            uvicorn entry
```

## Conventions

- Pydantic v2 only. `datetime.now(timezone.utc)`. Relative imports within `app/`.
- Verify `pydantic-ai` class/kwarg names against the installed version before use.
- Every bug fix gets a test. The suite is fully offline (in-memory product fake,
  mocked LLM). No network.
- No dead code, no redundancy.

## Commands

```bash
python main.py     # run the POC on :8000
pytest             # offline suite
```
