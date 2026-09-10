# Refactor Progress

Legend: `[ ]` todo · `[~]` in progress · `[x]` done · `[!]` blocked/needs user

## Phase 0 — Baseline & safety net
- [x] Create `refactor` branch
- [x] Create `.claude/refactor/` tracking docs
- [x] Create `dump/` folder + git-ignore it
- [x] venv `clothenv/` + `pip install -r requirements.txt` (clean, `pip check` OK)
- [x] Run `pytest`, record baseline in BASELINE.md -> **58 passed**
- [x] Confirm `backend/chatbot/agent.py` imports (finding #14) -> RESOLVED, imports fine
- [x] Confirm app boots -> lifespan + real Atlas verified via TestClient context manager
- [x] Pin dependency versions -> `requirements.lock.txt` (curated trim deferred to P1)
- [x] Commit: "P0: baseline, lockfile, tracking scaffold + P0.5 lazy DB indexes"

### Phase 0.5 — pulled forward from P7 (unblocks offline baseline)
- [x] `backend/database.py`: `create_index` at import -> `ensure_indexes()` function
- [x] `main.py` + both services: FastAPI `lifespan` calls `ensure_indexes()` on startup
- [x] pytest green (58), all 3 apps import, monolith full boot against Atlas OK

## Phase 1 — Dependency & config hygiene
- [x] requirements.txt: dropped jinja2 (0 dependents) + [tavily] (0 code refs);
      collapsed logfire->logfire[fastapi]; pydantic-ai(full)+slim[tavily] -> slim[openai,groq];
      pinned everything ==; new requirements-dev.txt (pytest + nest-asyncio)
- [x] backend/config.py: single load_dotenv, pydantic-settings Settings, SUPPORT_PHONE,
      is_placeholder(); added allowed_origins + ingestion_service_url + guard model names
- [x] Removed redundant load_dotenv() in database.py, guardrails.py, google_auth.py, llm_gateway.py
      (all now route through backend.config)
- [x] main.py + both services: logfire token via settings.logfire_write_token;
      CORS + /config via settings (services no longer read os.getenv directly)
- [x] Fixed REPLACE_WITH vs .env.example: .env.example now uses REPLACE_WITH_* consistently;
      is_placeholder() is the shared guard (case-insensitive, handles blank)
- [x] pytest green -> 58 passed; config smoke OK; Portkey still detected as configured
- [x] Fresh-venv validation of trimmed requirements: all 3 apps + chatbot import
- [x] Commit -> ba835f5

## Phase 2 — Dead code: backend -> 4268629
- [x] dump + remove uploads dir + /uploads mount (main.py, services/retrieval/main.py);
      `import os` now unused in both -> removed; StaticFiles import moved to top of main.py
- [x] Remove inStock/rating/reviews in get_products + fix test_products.py
- [x] Collapse model_dump()/.dict() -> .model_dump() (orders.py, cart.py, products_bulk.py)
- [x] Remove StoreDeps class-based Config (also clears the last pydantic deprecation warning)
- [x] HasProducts evaluator -> dumped (not re-wired: would couple manual evals to live Atlas)
- [x] REFUSAL_MESSAGE constant in config.py; guardrails + chatbot.py error fallback use it
      (agent.py system-prompt dedup deferred to P8 - sensitive multi-line string)
- [x] pytest green -> 58 passed, warnings 2 -> 1 (only the third-party Starlette one left)
- [x] boot smoke: all 3 apps, /products shape clean, frontend still served
- [x] Commit (see git log)

## Phase 3 — Dead code: frontend -> 931c7ad
- [x] index.html: drop broken /vite.svg favicon (-> inline data-URI SVG, no more 404)
      + drop bolt.new og/twitter meta
- [x] Frontend/.gitignore: deleted (fully redundant with root .gitignore; no Node build)
- [x] Cart.js: remove setTimeout(() => renderHeader(), 100) no-op line
- [~] Dead hamburger button -> DEFERRED to P6 (owns the responsive-nav rebuild wholesale;
      removing + re-adding across phases is churn)
- [~] Hero CTA buttons ("Shop Now"/"View Catalog") -> DEFERRED to P6 (visible UI; will be
      wired to scroll-to-products rather than deleted)
- [x] node available (v22.16.0): all Frontend/src/*.js parse clean
- [x] pytest 58 passed; static serve smoke (/, /src/main.js, /src/style.css) all 200
- [x] Commit (see git log)

## Phase 4 — Bugs: backend -> 3bcfffd
- [x] PUT /products/{id}: backend was already multipart-only; added `_object_id`
      helper, dropped the broad try/except, added "no fields -> 400". Frontend side
      of D1 (always send FormData) is in P5. Tests: nonexistent(404), no-fields(400),
      json-body(400 + unchanged).
- [x] Narrow except in update_product/delete_product -> `_object_id()` (bson InvalidId);
      real errors no longer masked as "Invalid ID format"
- [x] add_to_cart merge-quantity via $inc + FakeCollection $inc support + test
- [x] user.get("password_hash") in login/update_profile/delete_account;
      passwordless (Google) accounts -> clear 400 on profile-edit / delete + 2 tests
- [x] GET /products/{id} (+ _public_product helper, reused by get_products);
      wired into retrieval service too; 3 tests (ok / 404 / 400)
- [x] pytest -> **67 passed** (58 + 9); retrieval single-product verified vs Atlas
- [x] DECISIONS.md D8 logs every behaviour change; FOLLOWUPS.md created
- [x] Commit (see git log)

## Phase 5 — Bugs: frontend API layer -> 4e35f65
- [x] api/http.js request() helper (write/admin flags, JSON|FormData body,
      res.ok check, Error(detail) on failure/network)
- [x] Refactored api/{auth,products,cart,orders,chat}.js onto it; barrel exports request
- [x] Callers fixed: productForm.js (add/update now catch + real messages; shared
      collectAdminForm/buildProductFormData helpers; D1 -> always FormData),
      productList.js (delete: confirm dialog + catch), quickActions.js (error detail)
- [x] main.js: startup try/catch so router() always runs
- [x] checkIsAdmin / getGoogleClientId swallow errors -> safe defaults
- [x] Home/ProductDetail/Admin: minimal try/catch -> [] (real error UI is P6)
- [x] node --check all Frontend/src/*.js clean; Node smoke harness 36/36
- [x] backend pytest still 67 passed
- [x] Commit (see git log)

## Phase 6 — Frontend state & rendering -> committed
- [x] App shell: index.html now #site-header + #app + #chatbot-root. Pages render
      into #app only (dropped the `${renderHeader()}` prepend from all 5).
- [x] cartItemCount single source of truth: services/cartCount.js
      (setCartCount/refreshCartCount) is the only writer; header repaints on change.
      Wired into startup, add-to-cart, clear, checkout, login/logout/register/google.
- [x] header patch helper: components/Header.js mountHeader() + event wiring
      (data-nav buttons, no more inline onclick / window.handleCatClick global)
- [x] chatbot persistent global mount: components/Chatbot.js mountChatbot() into
      #chatbot-root; all chat logic moved out of Home.js; re-renders only the
      chatbot on state change (was: full renderHome() x3 per message). Fixed the
      typing-indicator position + added scroll-to-bottom + disabled-while-loading.
- [x] category + price nav via hash: #/?cat=men&min=500&max=1000; new
      services/nav.js (navigate + currentRoute, dependency-free); Home reads the
      URL, filter/nav buttons navigate(). Back button + refresh now preserve view.
- [x] responsive nav: .menu-btn shows < 1024px, .nav becomes a dropdown on
      .header.nav-open, #menuToggle wired. (P3-deferred hamburger, now real.)
- [x] Hero CTAs wired -> smooth-scroll to the product grid (P3-deferred).
- [x] ProductDetail: fetchProduct(id) (new P4 endpoint) + real "couldn't find
      that product" empty state (was infinite "Loading...").
- [x] escapeHtml() helper (utils/escapeHtml.js) applied to every user/DB string:
      Home cards, ProductDetail, Chatbot messages+recs, Cart items, admin
      productList, profileCard, orderHistory, productForm inputs, Header username.
- [x] reset transient UI on navigation: state.ui {profileEditOpen, profileDeleteOpen,
      authMode} + resetTransientUi() called by router when the path's page changes.
      Profile.js + authForms.js no longer use module-level let flags.
- [x] router() is now async and awaits the page render (predictable + testable).
- [x] node --check clean; render smoke harness 16/16 (module graph, header,
      chatbot, cart-count=summed-qty, hash filters, HTML escaping, not-found,
      transient-ui reset); backend still 67 passed; shell + all new files serve.
- [x] Commit (see git log)

## Phase 7 — Backend structure
- [x] FastAPI lifespan for index creation -> DONE in P0.5 (20708f5)
- [x] Kill triple route registration -> read_router/write_router per module; the
      3 apps mount the halves they serve. Parity verified (23 ops, no overlap). -> 05c38b9
- [x] chatbot.py: 3x print() -> logfire.exception() (matches the observability theme)
- [x] agent.py: system prompt -> SYSTEM_PROMPT constant, refusal sentence now
      interpolates config.REFUSAL_MESSAGE (P2-deferred dedup done)
- [x] settings.agent_model_name (env AGENT_MODEL_NAME) — the suspicious "qwen3.6-27b"
      is now overridable without a code edit (default unchanged; see FOLLOWUPS #3)
- [x] models.py: fixed "## type hiniting" typo; grouped catalog vs accounts with
      section headers; documented that Product is the bulk-JSON shape only;
      added Field(ge=0) on prices and Field(ge=1) on quantities (previously unvalidated)
- [x] pytest 67 passed; `-W error::DeprecationWarning` on all 3 apps -> clean
- [x] Commit P7b (see git log)

## Phase 8 — Readability -> committed
- [x] Extracted the repeated inline-style patterns into style.css classes:
      .page/.page-{sm,md,lg}, .page-title, .card/.card--danger, .field, .full-width,
      .muted, .text-link, .card-heading, .list-row/.list-stack, .divider, .avatar/
      .avatar-fallback, .cart-item*, .cart-empty, .btn-danger-outline, .price-lg,
      .google-signin. Rewrote Cart.js, Profile.js, authForms.js, profileCard.js,
      orderHistory.js, dangerZone.js, googleSignIn.js, productForm.js, bulkImport.js,
      quickActions.js. Cart.js also split into renderCartItem/wireClearCart/wireBuyAll
      and parallelised its two startup reads. Remaining inline styles are 1-3 prop
      one-offs (flex:1, a margin) — not worth single-use classes.
- [x] Frontend error handling already consistent (try/catch + alert(err.message))
      from P5/P6; no gaps found.
- [x] Backend route docstrings accuracy pass: products.py ("demo data" -> real
      wording), cart.py (mention clear). The rest were already accurate.
- [x] node --check clean; render smoke 16/16; backend 67 passed.
- [x] Commit (see git log)

## Phase 9 — Documentation (done on request; standalone framing, no history)
- [x] Removed the old docs/ tree (numbered sub-folders, stale content) -> dump/p9-old-docs/
- [x] New flat docs/: README + 01-overview, 02-architecture, 03-frontend, 04-backend,
      05-database, 06-ai-assistant, 07-deployment, 08-glossary
- [x] Written as a standalone project explanation in plain language — no mention of
      any past state / migration; every architectural component broken down with
      "why it's there"; MongoDB's role, every GCP service (Cloud Run, Artifact
      Registry, IAM/Workload Identity Federation + service account) explained
- [x] 12 mermaid diagrams — all render clean via mermaid-cli
- [x] Root README.md rewritten as a real project README
- [x] commands.md rewritten to match the actual pipeline (GitHub Actions ->
      Artifact Registry -> Cloud Run via Workload Identity Federation)
- [x] cicd.yaml: fixed `pip install -r requirements.txt` -> `requirements-dev.txt`
      (pytest moved to dev in P1 and CI would have failed); trimmed the test-job
      env to just GROQ_API_KEY (MONGO_URI no longer needed to import); dropped the
      unused TAVILY_API_KEY from both deploys
- [x] pytest 67 passed
- [x] Commit (see git log)

### deps: unpin (done on request) -> 7752e9b
- [x] requirements.txt / requirements-dev.txt back to bare package names
- [x] requirements.lock.txt kept as an OPTIONAL fully-pinned snapshot (header added)
- [x] Fresh `uv venv clothenv` (Python 3.11.13): uv pip check clean, compileall clean,
      all imports clean, node --check clean, smokes pass, pytest 67 passed

## Phase 10 — Final verification
- [ ] Full pytest green
- [ ] Manual click-through: every page + flow
- [ ] Smoke `python main.py` and `docker-compose up`
- [ ] SUMMARY.md written
- [ ] Await user sign-off before deleting dump/
