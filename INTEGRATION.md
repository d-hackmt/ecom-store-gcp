# How the AI got integrated — `01-store-only` → `main`

This is a teaching reference: it shows, file by file, exactly what was added
on top of the plain store (`01-store-only`) to produce the full integrated
product (`main`). Read it as "here is every place the chatbot touches the
codebase" — useful for a live walkthrough of the integration.

A couple of things got refined *after* the initial merge (a dedicated image
endpoint, a couple of extra `logfire` log lines, disabling online evals by
default) — those are noted where they show up, so you don't mistake "recent
cleanup" for "the original POC merge."

---

## 1. Dependencies — `requirements.txt`

`01-store-only` has no AI dependencies at all. `main` adds two new sections
at the bottom of the same file:

```
# --- AI shopping assistant ---
pydantic-ai-slim[openai,groq]    # agent + OpenAI-compatible / Groq model providers
pydantic-evals                   # offline eval suite + live online evaluators
groq                             # guardrail models, called directly (AsyncGroq)
openai                           # guardrail models via the Portkey gateway (AsyncOpenAI)

# --- Observability ---
logfire[fastapi]                 # tracing + FastAPI / Pydantic / Pydantic-AI instrumentation
```

Nothing in the store's own dependencies changed — this is pure addition.

## 2. Environment variables — `.env.example`

`01-store-only`'s `.env.example` only has `MONGO_URI` and `GOOGLE_CLIENT_ID`.
`main` adds:

| Variable | Required? | What it's for |
|----------|-----------|----------------|
| `GROQ_API_KEY` | **Yes** — the app won't even start without it | every language-model call (the agent + both guardrail models) |
| `LOGFIRE_API_KEY` (or `LOGFIRE_TOKEN`) | No | tracing + eval score visibility; silent no-op without it |
| `PORTKEY_API_KEY`, `PORTKEY_GROQ_PROVIDER` | No | optional gateway in front of Groq for extra logging |

## 3. Settings — `backend/config.py`

`01-store-only`'s `Settings` class only has `mongo_uri` and `google_client_id`.
`main`'s version is the same file, with these fields and constants added:

```python
# Customer-care number the chatbot and guardrail refusals point users to.
SUPPORT_PHONE = "546464434"

# The single canonical refusal sentence — used by the guardrails, the agent's
# system prompt, and anywhere else the assistant declines a request.
REFUSAL_MESSAGE = (
    f"Sorry, I can't help with that. For assistance, contact our customer care at {SUPPORT_PHONE}."
)
```

and inside `Settings`:

```python
groq_api_key: str | None = None

portkey_api_key: str = ""
portkey_groq_provider: str = "groq"

agent_model_name: str = "openai/gpt-oss-20b"
guard_model_name: str = "openai/gpt-oss-safeguard-20b"
prompt_guard_model_name: str = "meta-llama/llama-prompt-guard-2-86m"

logfire_token: str | None = None
logfire_api_key: str | None = None
online_evals_enabled: bool = False   # off by default — see docs/06-ai-assistant.md

@property
def logfire_write_token(self) -> str | None:
    return self.logfire_token or self.logfire_api_key
```

Everything else in `config.py` — `mongo_uri`, `google_client_id`, the
`is_placeholder()` helper — is untouched.

## 4. A brand-new folder — `backend/chatbot/`

This entire folder does not exist on `01-store-only`. It's dropped in
unchanged from `02-chatbot-poc`'s `app/chatbot/` (the two are kept
byte-for-byte identical, one small difference noted below):

| File | Job |
|------|-----|
| `agent.py` | The Pydantic AI agent: system prompt + the one `search_products` tool it's allowed to call. |
| `guardrails.py` | The two Groq safety-model checks (input guard + output guard). |
| `pipeline.py` | `run_chat(message) -> dict` — guards → agent → guard → shape the response. The one function everything else calls. |
| `online_evals.py` | **Main-only** — the POC doesn't ship this file at all. Defines the live evaluators that *can* be attached to the agent (off by default, see `online_evals_enabled` above). |

`agent.py` has one conditional block that only exists because of this file:

```python
_capabilities = []
if settings.online_evals_enabled:
    from .online_evals import online_evaluation
    _capabilities = [online_evaluation]
```

This is the one place `agent.py` reads a setting the POC doesn't have — the
import only happens when online evals are turned on, so the POC (which
doesn't ship `online_evals.py`) never tries to import it.

## 5. A new helper — `backend/utils/llm_gateway.py`

New file. Resolves whether Groq calls should be routed through Portkey
(`is_portkey_configured()`) and rewrites model names for Portkey's syntax
(`resolve_model_name()`). Both `agent.py` and `guardrails.py` import from here.

## 6. A new route — `backend/routes/chatbot.py`

New file, the entire HTTP layer for the assistant:

```python
from fastapi import APIRouter, Body
from ..chatbot.pipeline import run_chat

read_router = APIRouter(prefix="/chat", tags=["Chatbot"])
write_router = APIRouter(prefix="/chat", tags=["Chatbot"])   # stays empty — chat never writes

@read_router.post("")
async def chat_bot(data: dict = Body(...)):
    return await run_chat(data.get("message", ""))
```

Same `read_router`/`write_router` pattern every other route file already
uses — nothing new to learn here, just one more module following the
existing convention.

## 7. A new offline eval suite — `backend/evals/`

New folder, `chatbot_evals.py` + `__init__.py`. A hand-written dataset of 10
example conversations run against the *real* agent on demand
(`python -m backend.evals.chatbot_evals`) — see [docs/06-ai-assistant.md](docs/06-ai-assistant.md)
for the full list of cases. Nothing on `01-store-only` resembles this.

## 8. Wiring it into the app — `main.py`

This is the one file that ties everything above together. Same file as
`01-store-only`'s, with these additions:

**New imports** (top of file):
```python
import logfire
...
from backend.routes import products, products_bulk, orders, cart, chatbot, auth, google_auth, profile
#                                                        ^^^^^^^ new
from backend.config import settings   # new — 01-store-only's main.py never imports settings
```

**New block before the app is created** — configures Logfire so a startup
failure gets traced too:
```python
logfire.configure(
    send_to_logfire='if-token-present',
    token=settings.logfire_write_token,
)
```

**New instrumentation calls right after `app = FastAPI(...)`:**
```python
logfire.instrument_fastapi(app)
logfire.instrument_pydantic()
logfire.instrument_pydantic_ai()   # agent run traces + online-evaluation events
```

**One word added to the route-mounting tuple:**
```python
ROUTE_MODULES = (products, products_bulk, orders, cart, chatbot, auth, google_auth, profile)
#                                                  ^^^^^^^ new — same loop mounts its read_router + write_router like every other module
```

*(The `try/except` around `ensure_indexes()` in the lifespan handler is a
later refinement for startup-failure visibility, not part of the original
chatbot merge — but it's in `main.py` today, so it's worth knowing it's there.)*

## 9. The frontend — the chat widget

Four small changes, all additive:

- **`Frontend/index.html`** — one new line: `<div id="chatbot-root"></div>`, sitting next to `<main id="app">`. The widget lives outside the router's DOM tree so it survives page navigation.
- **`Frontend/src/components/Chatbot.js`** — new file. The whole widget: renders the toggle button, the message window, calls the send/clear handlers.
- **`Frontend/src/services/api/chat.js`** — new file, one function: `sendChatMessage(message)` → `POST /chat`.
- **`Frontend/src/main.js`** — two additions to an existing file:
  ```js
  import { mountChatbot } from './components/Chatbot.js';   // new import
  ...
  mountChatbot();   // new call, inside the DOMContentLoaded handler, before the router runs
  ```
- **`Frontend/src/style.css`** — one new block of `.chatbot-*` rules appended (container, toggle button, window, header, messages, input, typing indicator) — pure addition, nothing existing is touched.

Product cards that the chatbot recommends reuse the storefront's own image
endpoint (`/products/{id}/image`) — no separate image-handling code needed
for chat results.

## 10. Documentation-only additions

- `docs/06-ai-assistant.md` — full walkthrough of the pipeline (this doc numbers itself 6; `01-store-only`'s deployment doc is numbered 6 there instead, since it has no AI doc to make room for).
- `docs/STORY.md` — the three-branch narrative this whole repo is built around.

---

## The one-sentence version

Take the plain store, add one folder (`backend/chatbot/`) plus two small
files (`llm_gateway.py`, `routes/chatbot.py`), add a handful of settings and
one dependency block, mount one more router in `main.py`, and drop a chat
widget into the frontend that talks to `POST /chat` — that's the entire
integration surface.
