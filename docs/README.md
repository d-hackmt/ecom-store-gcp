# LUXE — Documentation

LUXE is an online clothing store. You browse Men / Women / Kids clothing, filter
by price, add things to a cart, and place an order with just an email.

These docs explain the whole thing in plain language. Read them in order if you
are new:

| # | Page | What it covers |
|---|------|----------------|
| 1 | [Overview](01-overview.md) | What the project is, the full technology stack, and why each piece is there |
| 2 | [Architecture](02-architecture.md) | How all the parts fit together, and what happens on a request |
| 3 | [Frontend](03-frontend.md) | The storefront the shopper sees — how the pages, routing and state work |
| 4 | [Backend](04-backend.md) | The API — every endpoint, organized into read and write route modules |
| 5 | [Database](05-database.md) | MongoDB's job, the four collections, and what a document in each looks like |
| 6 | [Deployment](06-deployment.md) | Google Cloud: every GCP service used, the container image, and the automated deploy pipeline |
| 7 | [Glossary](07-glossary.md) | Every technical term used in these docs, in one sentence each |

## The one-paragraph version

A **browser** loads a plain JavaScript storefront. It talks to a **FastAPI**
(Python) backend over a small JSON API. The backend keeps all its data —
products, carts, orders, user accounts — in **MongoDB**. In production the app
runs as two containers on **Google Cloud Run**.
