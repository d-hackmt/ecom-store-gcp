# LUXE — Documentation

LUXE is an online clothing shop with an AI shopping assistant built in.
You browse Men / Women / Kids clothing, filter by price, add things to a cart,
place an order with just an email, and — if you'd rather not click through
filters — you can simply *ask* the assistant ("show me men's shirts under
₹2000") and it fetches real products from the catalog for you.

These docs explain the whole thing in plain language. Read them in order if you
are new:

| # | Page | What it covers |
|---|------|----------------|
| — | [Story](STORY.md) | How this repo's three branches tell a Forward-Deployed-AI-Engineer story |
| 1 | [Overview](01-overview.md) | What the project is, the full technology stack, and why each piece is there |
| 2 | [Architecture](02-architecture.md) | How all the parts fit together, and what happens on a request |
| 3 | [Frontend](03-frontend.md) | The storefront the shopper sees — how the pages, routing and state work |
| 4 | [Backend](04-backend.md) | The API — every endpoint, organized into read and write route modules |
| 5 | [Database](05-database.md) | MongoDB's job, the four collections, and what a document in each looks like |
| 6 | [AI Assistant](06-ai-assistant.md) | The shopping chatbot: how it turns a sentence into a database query, and the safety guardrails around it |
| 7 | [Deployment](07-deployment.md) | Google Cloud: every GCP service used, the container images, and the automated deploy pipeline |
| 8 | [Glossary](08-glossary.md) | Every technical term used in these docs, in one sentence each |

## The one-paragraph version

A **browser** loads a plain JavaScript storefront. It talks to a **FastAPI**
(Python) backend over a small JSON API. The backend keeps all its data —
products, carts, orders, user accounts — in **MongoDB**. When a shopper talks to
the assistant, the backend hands the message to a **Pydantic AI** agent running
on **Groq**'s language models; the agent calls one tool, `search_products`,
which runs a MongoDB query and returns matches. Two lightweight **guardrail**
models check the message on the way in and the reply on the way out. Everything
is traced with **Pydantic Logfire**. In production the app runs as a single
container on **Google Cloud Run**.
