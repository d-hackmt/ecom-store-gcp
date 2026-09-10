# CLAUDE.md — LUXE (`01-store-only`)

## What this branch is

The LUXE online clothing store **with no AI** — FastAPI + MongoDB + a
vanilla-JS storefront, cart, orders, accounts, Google sign-in, admin.

It is **branch 1 of 3**, a frozen snapshot in a Forward-Deployed-AI-Engineer
story. The `main` branch has the full picture (`docs/STORY.md` there).

| Branch | Scope |
|--------|-------|
| `main` | Full integrated product: store + AI + guardrails + evals. Source of truth. |
| `01-store-only` | **← this branch.** The plain store. Frozen. |
| `02-chatbot-poc` | The standalone chatbot POC. Frozen. |

## Scope rule — do not add AI here

This branch must stay AI-free. **Do not** add `pydantic-ai`, `pydantic-evals`,
`groq`, `openai`, `logfire`, a `backend/chatbot/` package, a `/chat` route, or a
chat widget. Anything like that belongs on `main`. If a task seems to need AI
here, it's the wrong branch — stop and check with the user.

`main` is the source of truth. This branch is derived and frozen; a change here
does not flow back.

## Architecture

- `backend/` — the FastAPI app. One package, three entrypoints:
  - `main.py` — the monolith (storefront + every endpoint). Default.
  - `services/retrieval/main.py` — read endpoints + storefront.
  - `services/ingestion/main.py` — write endpoints.
- `backend/routes/*.py` — each module exposes `read_router` + `write_router`;
  entrypoints mount the half they serve.
- `backend/config.py` — the only place `.env` is read. One typed `Settings`
  (`MONGO_URI`, `GOOGLE_CLIENT_ID`, plus split-mode CORS settings).
- `Frontend/` — vanilla JS ES modules, no build step. `escapeHtml()` on every
  interpolation of user/DB text.

## Conventions

- Pydantic v2 only. FastAPI `lifespan=`. `datetime.now(timezone.utc)`.
- Relative imports within `backend/`.
- Every bug fix gets a test. The suite is fully offline (in-memory DB fake,
  `tests/conftest.py`). No network.
- No dead code, no redundancy. Removed code goes away, not commented out.

## Commands

```bash
python main.py     # run the monolith on :8000
pytest             # full offline suite
```
