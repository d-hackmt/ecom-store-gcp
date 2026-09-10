# 👕 ClothStore AI

An online clothing shop with an **AI shopping assistant** built in.

Browse Men / Women / Kids clothing, filter by price, add to a cart, and check
out with just an email. Or skip the filters entirely and *ask*: type
*"men's shirts under ₹2000"* into the chat widget and it fetches real products
from the catalog for you.

| | |
|---|---|
| **Storefront** | Plain JavaScript + CSS — served as‑is, no build step |
| **Backend** | FastAPI (Python) |
| **Database** | MongoDB Atlas |
| **AI assistant** | Pydantic AI agent on Groq models, with input/output safety guardrails |
| **Observability** | Pydantic Logfire |
| **Hosting** | Two containers on Google Cloud Run, deployed by GitHub Actions |

## Features

- **Catalog** — three categories, price‑range filter, per‑product sizes & colours.
- **Cart & checkout** — add to cart, "Buy All Now"; orders are keyed by email
  (a real one if you signed in, an auto‑generated guest one if you didn't).
- **Accounts** — email + password *or* Sign in with Google; edit profile,
  upload an avatar, view order history, delete the account.
- **AI assistant** — natural‑language product search, available on every page,
  wrapped in guardrails that block prompt‑injection and unsafe content.
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

### Run it the way production does (two services)

```bash
docker-compose up
# storefront + reads  → http://localhost:8000
# writes              → http://localhost:8001
```

## Tests

```bash
uv pip install -r requirements-dev.txt   # adds pytest
pytest
```

The suite runs **fully offline** — every database and language‑model call is
faked, so it is fast, free, and never touches Atlas or Groq. A pre‑push git hook
runs it automatically; activate it once after cloning:

```bash
git config core.hooksPath githooks
```

## Documentation

Everything — architecture, each component in plain language, the deployment
pipeline, a glossary — is in **[`docs/`](./docs/README.md)**.

| | |
|---|---|
| [Overview](docs/01-overview.md) | What it is, the full stack, why each piece |
| [Architecture](docs/02-architecture.md) | How it fits together + request walkthroughs |
| [Frontend](docs/03-frontend.md) · [Backend](docs/04-backend.md) · [Database](docs/05-database.md) | Each layer in detail |
| [AI Assistant](docs/06-ai-assistant.md) | The chatbot and its guardrails |
| [Deployment](docs/07-deployment.md) · [`commands.md`](commands.md) | Google Cloud, and the exact setup commands |
| [Glossary](docs/08-glossary.md) | Every term, one sentence each |

## License

MIT.
