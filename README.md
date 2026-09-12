# 👕 LUXE

An online clothing store. Browse Men / Women / Kids clothing, filter by price,
add to a cart, and check out with just an email.

> **Branch 1 of 3.** This is the LUXE store on its own — no AI. It's the
> starting point of a Forward-Deployed-AI-Engineer story: see the
> [`main`](../../tree/main) branch for the full picture (`docs/STORY.md` there),
> and [`02-chatbot-poc`](../../tree/02-chatbot-poc) for the assistant POC.

## Stack

| | |
|---|---|
| **Storefront** | Plain JavaScript + CSS — served as-is, no build step |
| **Backend** | FastAPI (Python) |
| **Database** | MongoDB Atlas |
| **Hosting** | Google Cloud Run (single container), deployed by Google Cloud Build |

## Features

- **Catalog** — three categories, price-range filter, per-product sizes & colours.
- **Cart & checkout** — add to cart, "Buy All Now"; orders are keyed by email
  (a real one if you signed in, an auto-generated guest one if you didn't).
- **Accounts** — email + password *or* Sign in with Google; edit profile,
  upload an avatar, view order history, delete the account.
- **Admin** — add / edit / delete products, plus a bulk importer that takes an
  Excel sheet and a zip of images.

## Quick start

```bash
# 1. Configuration
cp .env.example .env          # then fill in MONGO_URI

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

Architecture, each layer in plain language, the deployment pipeline, and a
glossary are in **[`docs/`](./docs/README.md)**.

## License

MIT.
