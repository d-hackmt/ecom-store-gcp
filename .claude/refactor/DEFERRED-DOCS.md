# Deferred to Phase 9 (docs) — user will trigger

Do NOT touch these until the user says "do the docs". Logged here so nothing is lost.

## Explicit user asks
- **`commands.md`** — check correctness. Current state: describes a hand-written
  `cloudbuild.yaml` single-service Google Cloud **Build** trigger setup. Reality:
  `.github/workflows/cicd.yaml` is a GitHub **Actions** pipeline deploying **two**
  services (ingestion + retrieval) to Cloud **Run** via Artifact Registry + Workload
  Identity Federation. `commands.md` is stale / inconsistent with the actual pipeline.
- Docs readability: analogies + mermaid style is good; content accuracy is the problem.

## Known stale docs (from the earlier review, for the Phase 9 rewrite)
- `docs/README.md` — false "authentication has been removed" note; API table incomplete.
- `docs/03-frontend/01-main-js.md` — describes a non-existent older codebase.
- `docs/06-deployment/00-deployment.md` — wrong cloud (AWS EC2/ECR vs GCP Cloud Run).
- `docs/00-terminologies.md` — AWS references.
- `docs/02-backend/08-database.md` + `docs/04-database` — wrong `users` schema.
- `docs/{02-backend/09-models,05-models}` — `Order` missing `price`; auth models absent.
- `docs/02-backend/01-main-app.md` — "GET / welcome message", wrong file tree.
- `docs/02-backend/00-backend-overview.md` — wrong run command.
- Numbering gaps in `docs/02-backend/` (01,03..08,09); `04-database`/`05-models` duplicate content.
- Missing diagrams: auth flow, guardrail pipeline, split-services topology, checkout.

## Refactor changes that WILL need doc updates (track as we go)
- P0.5: `ensure_indexes()` + lifespan (was import-time `create_index`).
- P1: `backend/config.py` single source of config; `.env.example` now uses REPLACE_WITH_*
  placeholders; `requirements.txt` trimmed + pinned, new `requirements-dev.txt`.
- (more appended per phase)
P9 docs done (2026-09-04)
