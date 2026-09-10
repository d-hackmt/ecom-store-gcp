# Session summary — `01-store-only`

Changes made while getting `python main.py` to start on a fresh machine.

## Code / dependency changes

### `requirements.txt` — added `requests`
`backend/routes/google_auth.py` imports `google.auth.transport.requests`, which
requires the `requests` package at runtime. It was a transitive dependency that
happened to be present in some environments but was never declared, so a clean
install of `requirements.txt` produced:

```
ImportError: The requests library is not installed ... to use the requests transport.
```

Added one line under `# --- Authentication ---`:

```
requests                         # HTTP transport used by google-auth
```

### `cloudbuild.yaml` — inject runtime config into Cloud Run

The Cloud Run deploy step set no environment variables, and `.dockerignore`
keeps `.env` out of the image, so in the container `settings.mongo_uri` was
`None`. `MongoClient(None)` targets `localhost:27017`, `ensure_indexes()` in the
lifespan handler raised `ServerSelectionTimeoutError`, startup aborted, and the
container never bound its port:

```
ERROR: (gcloud.run.deploy) The user-provided container failed to start and
listen on the port defined provided by the PORT=8000 environment variable
```

Both runtime values are pulled from Secret Manager so nothing sensitive sits in
a committed file:

```
      - '--set-secrets'
      - 'MONGO_URI=MONGO_URI:latest,GOOGLE_CLIENT_ID=GOOGLE_CLIENT_ID:latest'
```

One-time GCP setup: create Secret Manager secrets `MONGO_URI` and
`GOOGLE_CLIENT_ID`, and grant the Cloud Run runtime service account
(`<projectNumber>-compute@developer.gserviceaccount.com`) the
`roles/secretmanager.secretAccessor` role.

### `Frontend/src/pages/profile/googleSignIn.js` — harden the client-id guard

The guard skipped setup only when the id contained `REPLACE_WITH`, but the
`.env.example` placeholder is `YOUR_GOOGLE_CLIENT_ID`, which slipped through and
let Google init run with a bogus id. Now it requires a real-looking id:

```
if (!clientId || !clientId.endsWith('.apps.googleusercontent.com')) return;
```

### `commands.md` — console-only deploy guide

Rewritten so every GCP step is done through the Cloud Console website, no
`gcloud` CLI:

- Enable **Secret Manager API**; new Phase 2 section to create the `MONGO_URI`
  and `GOOGLE_CLIENT_ID` secrets (and add new versions after a rotation).
- Synced the sample `cloudbuild.yaml` with the real one (`store-repo` / `store`
  names, the `--set-secrets` line); Artifact Registry repo name aligned to
  `store-repo`.
- Phase 4 IAM: added **Secret Manager Secret Accessor** to the runtime service
  account's roles.
- Phase 7 rewritten — config now comes from Secret Manager via `cloudbuild.yaml`,
  not hand-added plaintext env vars on the Cloud Run service.

## Security — exposed credentials

Commit `606cc48` committed the real `MONGO_URI` (with the DB password) to
`.env.example` and was pushed to `origin/01-store`. A later commit reverted the
file to placeholders, but the value remains in git history on GitHub.

- **Required:** rotate the MongoDB Atlas password, then update the `MONGO_URI`
  Secret Manager secret and local `.env`.
- The old Google OAuth client (`...glk232...`) was deleted; a new one replaced
  it. A client id is not a secret (browsers receive it), but it is no longer
  stored in `cloudbuild.yaml` either — it lives in the `GOOGLE_CLIENT_ID` secret.
- History rewrite (BFG / `git filter-repo` + force push) is optional; rotation is
  what actually neutralises the leak.
