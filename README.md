# 👕 LUXE

An online clothing store with an **AI shopping assistant** built in.

Browse Men / Women / Kids clothing, filter by price, add to a cart, and check
out with just an email. Or skip the filters entirely and *ask*: type
*"men's shirts under ₹2000"* into the chat widget and it fetches real products
from the catalog for you.

---

## This repo tells a story

LUXE is built the way a **Forward Deployed AI Engineer** takes an idea from
nothing to production: understand the client's existing system → prove the AI
idea in an isolated POC → harden it and integrate it, with evals and
observability. Each stage is a branch:

| Branch | Stage | What it is |
|--------|-------|------------|
| [`01-store-only`](../../tree/01-store-only) | **Discovery** — the client's existing app | The plain clothing store: FastAPI + MongoDB + a vanilla-JS storefront, cart, orders, accounts, admin. **No AI.** |
| [`02-chatbot-poc`](../../tree/02-chatbot-poc) | **POC** — prove it's possible | A standalone chatbot: connect to the product database, answer natural-language queries, wrapped in safety guardrails. One `POST /chat` + a tiny page. Nothing else. |
| `main` | **Integration** — production | `01` + `02`, merged. The POC's `chatbot/` package dropped into the store's backend, plus live evals and full tracing. **You are here.** |

The full narrative is in [`docs/STORY.md`](docs/STORY.md).

---

## Stack (this branch)

| | |
|---|---|
| **Storefront** | Plain JavaScript + CSS — served as-is, no build step |
| **Backend** | FastAPI (Python) |
| **Database** | MongoDB Atlas |
| **AI assistant** | Pydantic AI agent on Groq models, with input/output safety guardrails |
| **Evals** | Pydantic Evals — live evaluators on every real chat, plus an offline suite |
| **Observability** | Pydantic Logfire |
| **Hosting** | Google Cloud Run (single container), deployed by Google Cloud Build |

## Features

- **Catalog** — three categories, price-range filter, per-product sizes & colours.
- **Cart & checkout** — add to cart, "Buy All Now"; orders are keyed by email
  (a real one if you signed in, an auto-generated guest one if you didn't).
- **Accounts** — email + password *or* Sign in with Google; edit profile,
  upload an avatar, view order history, delete the account.
- **AI assistant** — natural-language product search on every page, wrapped in
  guardrails that block prompt-injection and unsafe content.
- **Admin** — add / edit / delete products, plus a bulk importer that takes an
  Excel sheet and a zip of images.

## Quick start

```bash
# 1. Configuration
cp .env.example .env          # then fill in MONGO_URI and GROQ_API_KEY (minimum)

# 2. Environment
uv venv clothenv              # (or: python -m venv clothenv)
source clothenv/Scripts/activate       # Windows;  clothenv/bin/activate on macOS/Linux
uv pip install -r requirements.txt     # (or: pip install -r requirements.txt)

# 3. Run — one process, storefront + API on http://localhost:8000
python main.py
```

Open <http://localhost:8000>. The interactive API reference is at
<http://localhost:8000/docs>.

## Documentation

Everything — the FDE story, architecture, each component in plain language, the
deployment pipeline, a glossary — is in **[`docs/`](./docs/README.md)**.

| | |
|---|---|
| [Story](docs/STORY.md) | How the three branches fit together |
| [Overview](docs/01-overview.md) | What it is, the full stack, why each piece |
| [Architecture](docs/02-architecture.md) | How it fits together + request walkthroughs |
| [Frontend](docs/03-frontend.md) · [Backend](docs/04-backend.md) · [Database](docs/05-database.md) | Each layer in detail |
| [AI Assistant](docs/06-ai-assistant.md) | The chatbot, its pipeline, and its guardrails |
| [Deployment](docs/07-deployment.md) · [`commands.md`](commands.md) | Google Cloud, and the exact setup commands |
| [Glossary](docs/08-glossary.md) | Every term, one sentence each |

## License

MIT.
