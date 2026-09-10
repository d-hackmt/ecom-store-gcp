# Pre-Refactor Baseline

Captured 2026-09-03, branch `refactor` off `main` @ `dc68b32`.

## Environment
- System Python: 3.13.7 (project historically targeted 3.10/3.11; Dockerfiles use 3.11-slim)
- venv: `clothenv/` (git-ignored, matches `githooks/pre-push` probe path)
- Full dependency snapshot: `requirements.lock.txt` (117 packages, `pip freeze`)

## Key direct dependency versions (as installed)
| Package | Version |
|---|---|
| fastapi | 0.141.1 |
| uvicorn | 0.52.4 |
| pydantic | 2.13.5 |
| pydantic-ai / pydantic-ai-slim / pydantic-evals | 2.38.0 |
| logfire | 4.41.0 |
| groq | 1.7.0 |
| openai | 3.7.0 |
| pymongo | 4.17.0 |
| bcrypt | 5.0.0 |
| python-dotenv | 1.2.3 |
| google-auth | 2.57.0 |
| Jinja2 | 3.1.6 (UNUSED — remove P1) |
| python-multipart | 0.0.32 |
| openpyxl | 3.1.5 |
| nest-asyncio | 1.6.0 (notebooks only — move to dev P1) |
| pytest | 9.1.1 |

## Test suite
- **Baseline: `58 passed`** in ~12s.
- IMPORTANT: baseline was only obtainable after a pre-emptive fix (see "Phase 0.5" below).
  Before that fix, `pytest` could not even *collect* offline — `backend/database.py`
  called `create_index()` at import time, forcing a live MongoDB connection. CI only
  passed because it injects real Atlas credentials.

## Finding #14 — RESOLVED
`backend/chatbot/agent.py` imports cleanly. `pydantic_evals.online`,
`pydantic_evals.online_capability.OnlineEvaluation`, and `Agent(..., capabilities=[...])`
all exist in pydantic-ai / pydantic-evals **2.38.0**. Not fabricated. No crash.

## App boot
- `import main` → OK (15 routes). `services.ingestion.main` / `services.retrieval.main` → OK.
- `TestClient(main.app)` as context manager → lifespan runs `ensure_indexes()` against
  real Atlas, `/config` → 200, `/products` → 200 with 10 real products. **Full boot verified.**

## Known deprecation warnings at baseline (to clear — D7)
1. `backend/chatbot/agent.py:29` — `class StoreDeps(BaseModel)` uses class-based
   `class Config` → Pydantic v2 wants `model_config = ConfigDict(...)`. Fix in P2
   (the config is `arbitrary_types_allowed=True`, which is also unnecessary → just delete).
2. `starlette/testclient.py:53` — `anyio.abc.BlockingPortal` alias. **Third-party
   (Starlette's own code), not ours.** Nothing to do; will clear on a Starlette bump.

No other DeprecationWarnings from our own code on import (`python -W error::DeprecationWarning -c "import main"`).

## Phase 0.5 — pre-emptive fix applied (pulled forward from P7)
`backend/database.py`: removed the two import-time `create_index()` calls; added
`ensure_indexes()`. `main.py`, `services/ingestion/main.py`, `services/retrieval/main.py`:
added a FastAPI `lifespan` handler that calls `ensure_indexes()` on startup.
Rationale: without this there is no offline baseline, which breaks the "pytest green at
every commit" rule. P7's remaining structure work (kill triple route registration,
logfire logging, models split) is unaffected.

## Behaviour to preserve (manual re-check list for Phase 10)
- Home: catalog loads, category filter, price filter, add-to-cart, chatbot (text + product).
- Product detail: view, add-to-cart, buy-now.
- Cart: list, clear, buy-all.
- Profile: register, login (email + username), Google sign-in, edit profile, avatar, delete.
- Admin: add / edit / delete / delete-all / bulk-JSON / bulk Excel+zip; admin gating (403).
- Chatbot guardrails: injection blocked, unsafe blocked, benign passes, fail-open on error.
- Deploy modes: `python main.py` (monolith) and `docker-compose up` (ingestion+retrieval).
