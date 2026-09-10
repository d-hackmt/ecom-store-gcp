# The Story — LUXE as a Forward-Deployed AI engagement

This project is shaped like the real work of a **Forward Deployed AI Engineer
(FDE)**: an engineer who embeds with a client and owns an AI feature end to end —
scoping it, proving it, writing the production code, wiring it into the client's
system, and keeping it honest with evals.

The standard arc is **Discovery → POC → Harden & Integrate**. LUXE walks through
it across three branches.

---

## Branch `01-store-only` — Discovery

**The situation.** The client, LUXE, already runs an online clothing store:
FastAPI, MongoDB Atlas, a plain-JavaScript storefront, cart, orders, accounts,
Google sign-in, an admin panel. It works. It's deployed on Google Cloud Run.
There is **no AI anywhere in it**.

**What the FDE does here.**

- Get the existing app running locally and in the client's cloud.
- Read the code. Learn the data: four MongoDB collections
  (`products`, `cart`, `orders`, `users`), how a product document is shaped, how
  identity works (a client-supplied email — no session tokens).
- Sit in on a client conversation: *"this is our app — we want a shopping
  assistant customers can just talk to. How does that even work?"*
- Come back with a proposal: a natural-language product search — turn a
  sentence into a database query — proven first in isolation, then integrated.

This branch is the client's app **exactly as it was handed over**. Nothing is
removed or simplified beyond taking the AI out — because there was never any AI
in it.

---

## Branch `02-chatbot-poc` — the POC

**The goal.** Show, in isolation, that the assistant idea works on the client's
real data — before touching the client's codebase.

**What's in it.**

- A slim copy of the product-reading layer, pointed at the same MongoDB.
- The assistant itself: a Pydantic AI agent with **one tool**, `search_products`,
  that builds and runs a MongoDB query and returns matches.
- Safety **guardrails**: two Groq safety models screen the incoming message, one
  screens the reply — so the POC can't be talked into leaking its prompt or
  saying something unsafe.
- One `POST /chat` endpoint and a single minimal HTML page that reuses the
  chat-widget look the real storefront will use.

**What's deliberately *not* in it.** No storefront, no cart, no orders, no
accounts, no admin, no evals, no deployment. A POC proves one thing.

The client sees it working against the live catalog, and approves.

> The chatbot code here is written as a **drop-in package** (`app/chatbot/`).
> Integration is meant to be close to copy-paste — that's the whole point of
> building it this way.

---

## Branch `main` — Integration

**The job.** Take the approved POC and make it part of the real product,
production-grade.

**What integration adds on top of `01-store-only`:**

- The POC's `chatbot/` package, dropped into `backend/chatbot/` essentially
  unchanged (`agent.py`, `guardrails.py`, `pipeline.py`).
- A thin `POST /chat` route (`backend/routes/chatbot.py`) that just calls the
  same `run_chat()` pipeline the POC's endpoint calls — one pipeline, two
  front doors.
- The chat widget on every storefront page.
- **Evals** — the beat after "client approved":
  - *Live:* `backend/chatbot/online_evals.py` attaches Pydantic Evals
    evaluators to the agent. After every real chat, in the background, they
    score the reply (non-empty? on-topic? invented no details?) and stream the
    scores to Logfire. `agent.py` attaches them when
    `settings.online_evals_enabled` is true — the default here, and the only
    difference from the POC, which defaults it off and doesn't ship this file.
  - *Offline:* `backend/evals/chatbot_evals.py` — a fixed set of example
    conversations run against the real agent on demand.
- **Full observability** — `logfire.instrument_fastapi` / `instrument_pydantic_ai`
  so every request and every agent step is a trace.

**What integration does *not* change.** The store. Cart, orders, accounts,
admin, the storefront — all of `01-store-only` — carry over untouched. The AI is
an addition, not a rewrite.

---

## How the branches relate

```
01-store-only ──┐
                ├──►  main   (01 + 02, integrated + evals + tracing)
02-chatbot-poc ─┘
```

- `main` is the **living** branch — the finished product.
- `01-store-only` and `02-chatbot-poc` are **frozen snapshots** — each is "what
  the client saw at that stage". They are derived from `main` by removing code,
  never maintained in parallel, so a change on `main` never forces edits on them.
- The overlap that matters — `agent.py`, `guardrails.py`, `pipeline.py` — is
  **byte-for-byte identical** between `02-chatbot-poc`'s `app/chatbot/` and
  `main`'s `backend/chatbot/`. The eval toggle lives in `config.py`, not in the
  package. So the "we just dropped the POC in" claim is literally true.
