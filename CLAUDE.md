# CLAUDE.md — LUXE

## What this repo is

An online clothing store with an AI shopping assistant, built as a
Forward-Deployed-AI-Engineer story told across three branches. Read
[`docs/STORY.md`](docs/STORY.md) first.

| Branch | Scope |
|--------|-------|
| `main` | **← this branch.** The full integrated product: store + AI + guardrails + evals + tracing. The only living branch. |
| `01-store-only` | The plain store, no AI. A frozen snapshot, derived from `main` by removing all AI code. |
| `02-chatbot-poc` | The standalone chatbot POC. A frozen snapshot, derived from `main`. |

**Branch rule:** `main` is the source of truth. `01` and `02` are derived and
frozen. A fix goes into `main` first; the demo branches are only re-derived if
explicitly asked. Never make a change on a demo branch expecting it to flow back.

## Architecture (this branch)

- `backend/` — the FastAPI app. One package, imported by three entrypoints:
  - `main.py` — the monolith (storefront + every endpoint). This is the default.
  - `services/retrieval/main.py` — read endpoints + storefront only.
  - `services/ingestion/main.py` — write endpoints only.
- `backend/routes/*.py` — each module exposes `read_router` + `write_router`;
  entrypoints mount the half they serve. A new endpoint is declared once.
- `backend/chatbot/` — the portable assistant package (kept in sync with
  `02-chatbot-poc`):
  - `agent.py` — the Pydantic AI agent + its `search_products` tool.
  - `guardrails.py` — the two Groq safety-model checks.
  - `pipeline.py` — `run_chat(message) -> dict`: guards → agent → guard → shape.
    Both `backend/routes/chatbot.py` and the POC's endpoint call this.
  - `online_evals.py` — live evaluators, attached only when
    `settings.online_evals_enabled` (on here, off in the POC).
- `backend/config.py` — the **only** place `.env` is read. One typed `Settings`.
- `Frontend/` — vanilla JS ES modules, no build step. `escapeHtml()` on every
  interpolation of user/DB text.

## Conventions

- **Python:** Pydantic v2 only (`model_dump()`, `model_config`, no `class Config`).
  FastAPI `lifespan=` (never `@app.on_event`). `datetime.now(timezone.utc)`.
  Match the docstring density and style of the file you're editing.
- **Imports:** relative within `backend/` (`from ..config import settings`).
- **AI libraries:** verify class/kwarg names against the installed version before
  using them (`pydantic-ai` / `pydantic-evals` move fast — see
  `.claude/history/` for what was checked and when).
- **Tests:** every bug fix gets a test. The suite is fully offline — DB is an
  in-memory fake (`tests/conftest.py`), the LLM boundary is mocked. No network.
- **No dead code, no redundancy.** Removed code goes away, not commented out.

## Commands

```bash
python main.py                       # run the monolith on :8000
pytest                               # full offline suite
python -m backend.evals.chatbot_evals   # offline eval suite (needs real GROQ_API_KEY + MONGO_URI)
```

## Not in scope on this branch

Nothing is off-limits here — `main` is the full system. (The *demo* branches
have their own `CLAUDE.md` with scope limits.)
