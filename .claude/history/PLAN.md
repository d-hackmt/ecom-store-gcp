# ClothStore Refactor — Frozen Plan

Branch: `refactor` (off `main`)
Scope: **code only** — Phases 0–8 + Phase 10 verification.
Docs (Phase 9) are **explicitly deferred** — do not touch `docs/`, `README.md`, or
inline doc prose beyond fixing factually-wrong docstrings that describe code being changed.

## Guiding rules

1. One phase at a time. Stop + report after each. `pytest` green at every commit.
2. Every bug fixed gets a test.
3. Pure-subtraction phases (2, 3, 8) must not change behavior.
4. Nothing is hard-deleted. Everything removed is moved to `dump/<phase>/<original-path>`
   first. `dump/` is git-ignored and is deleted only after Phase 10 sign-off.
5. Every non-obvious decision is logged in `DECISIONS.md`.
6. If a fix balloons beyond its phase, stop and re-plan.

## Deferred decisions (defaults chosen, see DECISIONS.md)

- D1 `PUT /products/{id}` → multipart-only.
- D2 Split services (ingestion/retrieval) → keep, fix the triple route registration.
- D3 Product name LUXE vs ClothStore → **no rebrand**; leave both, user decides later.
- D4 "Modernize" scope → vanilla JS, no build step; pydantic-settings + lifespan +
  shared fetch helper. No framework, no TS.

## Phases

- **P0** Baseline & safety net — venv, `pytest` baseline, confirm agent import, pin deps.
- **P1** Dependency & config hygiene — trim requirements, `backend/config.py`, one `load_dotenv`.
- **P2** Dead code: backend — uploads mount, inStock/rating/reviews, `.dict()` fallback, etc.
- **P3** Dead code: frontend — vite/bolt scaffold, `renderHeader()` no-op, dead hamburger.
- **P4** Bugs: backend — PUT content-type, broad excepts, cart merge, Google-account 401,
  add `GET /products/{id}`.
- **P5** Bugs: frontend API layer — `api/http.js` helper, `res.ok` everywhere, guard `main.js`.
- **P6** Frontend state & rendering — cartItemCount source of truth, header patch helper,
  chatbot global mount, hash-routed nav, responsive nav, ProductDetail not-found, escapeHtml.
- **P7** Backend structure — FastAPI lifespan, kill triple route registration, logfire logging,
  models split + validation.
- **P8** Readability — extract inline styles to CSS, consistent JSDoc/docstrings.
- **P9** Docs — DEFERRED, do not start.
- **P10** Final verification — full pytest, manual click-through, smoke both deploy modes.
