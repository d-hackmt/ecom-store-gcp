# SUMMARY — handoff snapshot

*Written for a fresh Claude session picking this up. Read `CLAUDE.md` and
`docs/STORY.md` too.*

---

## What this is

**LUXE** — an online clothing store with an AI shopping assistant, built to
demonstrate a **Forward-Deployed-AI-Engineer** engagement, told across three
git branches:

| Branch | Stage | Contents |
|--------|-------|----------|
| `01-store-only` | Discovery — the client's existing app | FastAPI + MongoDB + vanilla-JS storefront, cart, orders, accounts, Google sign-in, admin. **No AI, no observability.** |
| `02-chatbot-poc` | POC — prove it's possible | Standalone assistant: `app/chatbot/` (agent + guardrails + pipeline) + `POST /chat` + a one-page `web/` UI. Nothing else. |
| `main` | Integration — production | `01` + `02` merged: the POC's `chatbot/` package dropped into `backend/chatbot/`, a thin `/chat` route, the chat widget, **live + offline evals**, **Logfire tracing**. |

Repo: `https://github.com/d-hackmt/ecom-store-gcp-pvt` (private).

### Branch model (important)
`main` is the **only living branch** and the source of truth. `01` and `02` are
**frozen snapshots**, derived from `main` by removing code. A fix goes into
`main` first; the demo branches are only re-derived if explicitly asked. Never
edit a demo branch expecting the change to flow back.

Each branch has its own `CLAUDE.md` with a scope rule (e.g. `01-store-only`'s
says "do not add AI here").

---

## Current state — all branches pushed & green

| Branch | HEAD | Tests collect | `import main` |
|--------|------|---------------|--------------|
| `main` | `5da3d7f` | 68 | OK (22 routes, incl `/chat`) |
| `01-store-only` | `2c6f731` | 57 | OK (20 routes, no `/chat`) |
| `02-chatbot-poc` | `0bf387a` | 11 | OK (`/chat` only) |

"Tests collect" = `pytest --collect-only` with zero import errors. **The apps
have not been run** (see Constraints below) — only compile + import + collect
checks were done. The user runs `pytest` and the apps on a separate machine.

### Commit history (main)
```
5da3d7f  test: offline suite runs without GROQ_API_KEY
fbb330e  chore: remove stale .claude/history, trim ignore files
ce36dd9  P5: UI polish — warm-neutral palette + tokens, responsive fixes
db2c678  P4: finalize main — drop dead tavily setting, tighten STORY
8348856  P1: rebrand to LUXE, extract reusable chat pipeline, FDE-story docs
f83fc52  first commit (imported existing codebase)
```
`01-store-only` also has `96842a2` (P2: remove AI) and `45ab4dd` (P5 UI).
`02-chatbot-poc` also has `9160be9` (P3: build the POC) and `ec037de` (cleanup).

---

## Architecture facts

- **`backend/`** is one FastAPI package, mounted by three entrypoints:
  `main.py` (monolith, default), `services/retrieval/main.py` (reads + frontend),
  `services/ingestion/main.py` (writes). Each `backend/routes/*.py` exposes
  `read_router` + `write_router`; entrypoints mount the half they serve.
- **The reuse seam** — `backend/chatbot/`:
  - `agent.py` — Pydantic AI `Agent` + `search_products` tool (MongoDB query).
  - `guardrails.py` — two Groq safety models (prompt-guard + gpt-oss-safeguard).
  - `pipeline.py` — `run_chat(message) -> dict`: guards → agent → guard → shape.
    Both `backend/routes/chatbot.py` and the POC's `app/api.py` call this one function.
  - `online_evals.py` — Pydantic Evals live evaluators, attached in `agent.py`
    only when `settings.online_evals_enabled` (True on `main`, False in the POC).
  - **`agent.py`, `guardrails.py`, `pipeline.py` are byte-for-byte identical**
    between `main:backend/chatbot/` and `02-chatbot-poc:app/chatbot/`
    (verify: `git diff main:backend/chatbot/agent.py 02-chatbot-poc:app/chatbot/agent.py`).
    The eval toggle lives in `config.py`, not the package.
- **`backend/config.py`** — the only place `.env` is read. One typed `Settings`.
- **`Frontend/`** — vanilla JS ES modules, no build step. `escapeHtml()` on
  every interpolation of user/DB text. CSS uses `:root` design tokens
  (warm-neutral palette + one terracotta `--accent`).
- **Models on Groq** (all env-overridable): agent `openai/gpt-oss-20b`
  (production tier), guards `openai/gpt-oss-safeguard-20b` +
  `meta-llama/llama-prompt-guard-2-86m` (preview tier — no production
  equivalent), offline judge `openai/gpt-oss-120b`.
- **Portkey**: if `PORTKEY_API_KEY` is set, all Groq calls route through the
  Portkey gateway; otherwise direct. `utils/llm_gateway.py`.

---

## Environment / constraints

- **Installed venv is `clothenv/`, Python 3.14.6, uv-managed** (no `pip` inside
  it — use `uv` or `./clothenv/Scripts/python.exe -m ...`).
- Key pinned deps: `pydantic-ai(-slim) 2.38.0`, `pydantic-evals 2.38.0`,
  `fastapi 0.141.1`, `openai 3.7.0`, `groq 1.7.0`, `logfire 4.41.0`,
  `pydantic 2.13.5`. All API usage was checked against these versions
  (`OpenAIChatModel`, `OpenAIProvider`, `Agent(capabilities=[...])`,
  `result.output`, `chat.completions.create` — all current).
- **MongoDB Atlas is unreachable from the user's local network** — their ISP
  resets TLS on port 27017. The Atlas cluster + `0.0.0.0/0` allowlist are set
  up correctly; it just can't be reached from that connection. Works fine from
  GCP. `.env` `MONGO_URI` points at `clothing-store.o0t1bba.mongodb.net`
  (the user's own cluster). Do not try to "fix" the connection.
- The AI path (Groq direct + Portkey gateway + guard models + Logfire) is
  verified working from this environment.
- `.env` is gitignored and present locally. `.env.example` per branch lists the
  needed vars.

---

## Known items / possible next work

1. **`.gitattributes`** — not added. Every commit logs LF→CRLF warnings
   (Windows, `core.autocrlf=true`). Fix is `* text=auto eol=lf` + a one-time
   `git add --renormalize .`, but it touches every file's line endings — do it
   as its own commit if wanted.
2. **Stray folders when switching branches in one dir** — Python's `__pycache__`
   keeps deleted dirs alive after `git checkout`. Harmless (all gitignored),
   but for teaching use `git worktree add ../luxe-store 01-store-only` etc. so
   each branch has its own clean folder.
3. **`01-store-only` has no observability** by design (Logfire is what the FDE
   brings *with* the AI). If the demo wants request tracing on the "before"
   app, it's a ~10-line add but weakens that narrative beat.
4. **`docs/06-deployment.md` on `01-store-only`** still walks the full
   split-service "three-step dance" + Workload Identity Federation — accurate
   but heavy for "the client's simple app". Could be simplified.
5. **Deployment**: `.github/workflows/cicd.yaml` deploys the 2-service split to
   Cloud Run via Workload Identity Federation. Needs ~5 GitHub secrets (see
   `commands.md`). No Terraform (the user deprioritised new IaC work). The
   monolith (`main.py`) is the documented default run mode.
6. **`main`'s `.env.example`** uses `LOGFIRE_API_KEY`; the SDK prefers
   `LOGFIRE_TOKEN`. `config.py` accepts either — works, just legacy naming.

---

## How to run / check

```bash
# From repo root, with clothenv active (or prefix ./clothenv/Scripts/python.exe):
pytest                              # offline suite — no config needed now
python main.py                      # monolith on :8000  (needs a reachable MONGO_URI)
python -m compileall backend tests  # syntax check

# POC branch:
python main.py                      # POST /chat + web/ UI on :8000

# offline eval suite (main only, needs real GROQ_API_KEY + MONGO_URI):
python -m backend.evals.chatbot_evals
```

## Conventions (enforced, see CLAUDE.md)

Pydantic v2 only · FastAPI `lifespan=` · `datetime.now(timezone.utc)` ·
relative imports within `backend/` · every bug fix gets a test · fully-offline
test suite (in-memory DB fake + mocked LLM) · **no dead code, no redundancy** ·
verify `pydantic-ai`/`pydantic-evals` class names against the installed version.
