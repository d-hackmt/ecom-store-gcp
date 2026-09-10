# Decision Log

Format: ID · date · decision · rationale · affected files

---

## D1 · 2026-09-03 · `PUT /products/{id}` becomes multipart/form-data only
The frontend edit-without-image path sent JSON to an all-`Form(...)` endpoint → 422.
Options were (a) multipart-only, (b) JSON for fields + separate image endpoint.
Chose (a): matches `POST /products` (`add_product`), one content type, smallest change,
frontend already builds `FormData` for the image case.
Affected: `backend/routes/products.py`, `Frontend/src/services/api/products.js`,
`Frontend/src/pages/admin/productForm.js`.

## D2 · 2026-09-03 · Keep the ingestion/retrieval split, fix the triple registration
`.github/workflows/cicd.yaml` actively deploys both to Cloud Run, so the split is real,
not vestigial. Rather than delete it, Phase 7 restructures each route module to expose
read/write routers that all three apps (`main.py`, ingestion, retrieval) include, so a new
endpoint is declared once.
Affected: `backend/routes/*.py`, `services/ingestion/main.py`, `services/retrieval/main.py`.

## D3 · 2026-09-03 · No rebrand (LUXE vs ClothStore)
Frontend UI says "LUXE"; backend/README say "ClothStore". Renaming user-facing branding
is a product call, not a refactor call. Leaving both as-is. User to decide in a later pass.

## D4 · 2026-09-03 · "Modernize" = stdlib-level modernization only
pydantic-settings for config, FastAPI lifespan, a shared `fetch` wrapper on the frontend,
extract inline styles. NO framework migration, NO TypeScript, NO build step — the
"vanilla JS, served directly" architecture is a stated project goal.

## D5 · 2026-09-03 · venv named `clothenv/`
Matches the path the existing `githooks/pre-push` hook probes for. Already git-ignored.

## D7 · 2026-09-03 · No deprecated APIs (user directive)
Everything written/changed must match current library docs:
- FastAPI: `lifespan=` context manager, never `@app.on_event`.
- Pydantic v2: `model_config = ConfigDict(...)` / `field_validator`, never `class Config`
  or v1 `@validator`; `model_dump()` never `.dict()`.
- `datetime.now(timezone.utc)` never `utcnow()`.
- pydantic-ai / pydantic-evals / groq / openai: verify class + kwarg names against the
  version pinned in P0 before using them (e.g. `OpenAIChatModel` vs older `OpenAIModel`,
  the `Agent(...)` signature, the `pydantic_evals.online` surface from finding #14).
- pydantic-settings (separate package) for `BaseSettings`.

## D8 · 2026-09-03 · P4 behaviour changes (bug fixes — intentional)
- `POST /cart/add` now merges quantity into an existing (user, product) row via
  `$inc` instead of inserting a duplicate. FakeCollection.update_one gained `$inc`
  support to match.
- `PUT`/`DELETE /products/{id}`: invalid id -> 400 `"Invalid product ID"` (was
  `"Invalid ID format"`). The broad `except Exception` is gone, so a real DB error
  now surfaces as 500 instead of being mislabelled a 400.
- `PUT /products/{id}` with no updatable fields -> 400 `"No fields to update"`
  (previously an empty `$set` hit Mongo and 500'd, mislabelled 400). A JSON body
  yields no form fields, so it lands here too (documented by a test).
- New `GET /products/{id}` (monolith + retrieval service). Public read, like the list.
- `PUT /auth/profile` and `DELETE /auth/account` on a passwordless (Google) account
  -> 400 with a clear "uses Google Sign-In" message instead of a confusing
  401 "incorrect password". Letting Google users actually edit/delete via a fresh
  Google credential is a follow-up, noted in FOLLOWUPS.md.
- `login` / `update_profile` / `delete_account` read `user.get("password_hash")`
  (KeyError-safe for legacy docs); no change for normal accounts.

## D9 · 2026-09-04 · P5 frontend API layer
- New `Frontend/src/services/api/http.js` `request(path, opts)` is the single
  fetch path. Options: `method`, `body` (object -> JSON, FormData -> as-is),
  `headers`, `write` (-> ingestion service), `admin` (-> X-User-Email header).
  Always returns parsed JSON (or null); throws `Error(<backend detail>)` on any
  non-2xx or network failure.
- All 5 `api/*.js` modules rewritten to call `request()`. Barrel `api_v2.js`
  re-exports `request` too.
- `updateProduct(id, body, isFormData)` -> `updateProduct(id, formData)`. The
  admin edit form now always builds a FormData (D1 frontend half); the JSON path
  that 422'd/400'd is gone. `productForm.js` gained `collectAdminForm()` +
  `buildProductFormData()` helpers (shared by add & update).
- Callers that previously reported success regardless of HTTP status now catch
  and surface the real message: `productForm.js` (add/update), `productList.js`
  (delete — also gained a confirm dialog), `quickActions.js` (delete-all).
- `checkIsAdmin` and `getGoogleClientId` swallow failures and return safe
  defaults (false / '') — "unknown" must not throw during startup.
- `main.js` startup wrapped in try/catch so a slow/unreachable backend can't
  leave a blank page; `router()` always runs.
- Read callers with no error handling (Home, ProductDetail, Admin) got a minimal
  try/catch -> `[]` fallback. Real error UI is P6.
- `getCart`/`clearCart` now `encodeURIComponent` the email path segment (matches
  `getOrderHistory`; decodes identically server-side).
- Verified: 36/36 assertions in a Node smoke harness (request() behaviour +
  barrel exports + no circular-import breakage).

## D10 · 2026-09-04 · P6 frontend state & rendering
- App shell (`#site-header` / `#app` / `#chatbot-root`) so the header and chatbot
  persist across navigation instead of being re-templated into every page.
- `state.cartItemCount` is now written in exactly one module (`services/cartCount.js`)
  and is the **total item quantity** (sum of `quantity`), not the row count. Every
  auth transition (login/register/google/logout) refreshes it for the new session.
- Category + price filter live in the hash (`#/?cat=&min=&max=`) so the view is
  shareable and the back button works. `services/nav.js` holds `navigate` +
  `currentRoute`, kept free of imports so `router.js` and `Header.js` can both use it
  without a cycle. `window.handleCatClick` global removed.
- Chatbot re-renders only `#chatbot-root` on a chat state change (was: three full
  `renderHome()` calls — and three catalog refetches — per message). It is also now
  available on every page, not just Home.
- Transient per-page UI (profile edit/delete panels, auth login/register mode)
  moved from module-level `let` into `state.ui`, reset by `resetTransientUi()` which
  the router calls when the route's *page* changes (not on same-page re-renders).
- `router()` became `async` and awaits the page render — makes navigation
  deterministic and testable; hashchange handlers ignore the returned promise.
- `escapeHtml()` is applied at every interpolation of user/DB text. Chose explicit
  per-site escaping over an auto-escaping tagged-template (which would fight the
  many intentional-HTML interpolations like `${renderHero()}`).
- Responsive nav + Hero CTAs: the P3-deferred dead hamburger is now a working
  mobile menu toggle; "Shop Now" / "View Catalog" smooth-scroll to the grid.

## D6 · 2026-09-03 · `dump/` folder for all removals
Git-ignored. Mirrors original repo paths under `dump/pNN-<slug>/`. Deleted only after
Phase 10 sign-off. A `dump/MANIFEST.md` lists every moved file + why + the commit that removed it.
