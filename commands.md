# Deploying ClothStore to Google Cloud Run

This is the hands‑on companion to [`docs/07-deployment.md`](docs/07-deployment.md).
It walks through setting up the Google Cloud project so that the GitHub Actions
pipeline (`.github/workflows/cicd.yaml`) can build and deploy the two container
services on every push to `main`.

You need: a Google Cloud account with billing enabled, and the `gcloud` CLI
installed and logged in (`gcloud auth login`).

Throughout, replace `YOUR_PROJECT_ID` and `YOUR_GITHUB_ORG/YOUR_REPO` with your
own values. The region is `us-central1` (matches `cicd.yaml`).

---

## 1. Pick the project and enable the APIs

```bash
gcloud config set project YOUR_PROJECT_ID

gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  iamcredentials.googleapis.com \
  sts.googleapis.com
```

| API | Why |
|-----|-----|
| `run.googleapis.com` | Cloud Run — runs the containers |
| `artifactregistry.googleapis.com` | stores the Docker images |
| `iamcredentials.googleapis.com`, `sts.googleapis.com` | the keyless GitHub → GCP token exchange |

---

## 2. Create the Artifact Registry repository

The pipeline pushes images to a Docker repo called `clothstore`.

```bash
gcloud artifacts repositories create clothstore \
  --repository-format=docker \
  --location=us-central1 \
  --description="ClothStore container images"
```

---

## 3. Create the deploy service account

This is the identity the pipeline acts as.

```bash
gcloud iam service-accounts create clothstore-deployer \
  --display-name="ClothStore GitHub deployer"

DEPLOYER="clothstore-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com"

# Grant exactly what the pipeline needs
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:${DEPLOYER}" --role="roles/run.admin"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:${DEPLOYER}" --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:${DEPLOYER}" --role="roles/iam.serviceAccountUser"
```

---

## 4. Set up Workload Identity Federation (keyless auth)

This lets GitHub Actions authenticate **without** a downloaded service‑account
key.

```bash
# a pool to hold external identities
gcloud iam workload-identity-pools create github-pool \
  --location="global" \
  --display-name="GitHub Actions pool"

# a provider that trusts GitHub's OIDC tokens
gcloud iam workload-identity-pools providers create-oidc github-provider \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="GitHub OIDC" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --attribute-condition="assertion.repository=='YOUR_GITHUB_ORG/YOUR_REPO'"

# let this repo's workflows impersonate the deploy service account
PROJECT_NUMBER=$(gcloud projects describe YOUR_PROJECT_ID --format='value(projectNumber)')

gcloud iam service-accounts add-iam-policy-binding "${DEPLOYER}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github-pool/attribute.repository/YOUR_GITHUB_ORG/YOUR_REPO"
```

Get the provider resource name for the next step:

```bash
gcloud iam workload-identity-pools providers describe github-provider \
  --location="global" --workload-identity-pool="github-pool" \
  --format="value(name)"
# → projects/NUMBER/locations/global/workloadIdentityPools/github-pool/providers/github-provider
```

---

## 5. Add the GitHub repository secrets

**Repo → Settings → Secrets and variables → Actions → New repository secret.**

| Secret | Value |
|--------|-------|
| `GCP_PROJECT_ID` | `YOUR_PROJECT_ID` |
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | the provider resource name from step 4 |
| `GCP_SERVICE_ACCOUNT_EMAIL` | `clothstore-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com` |
| `MONGO_URI` | your MongoDB Atlas connection string |
| `GROQ_API_KEY` | from console.groq.com |
| `GOOGLE_CLIENT_ID` | OAuth client id (only if you want Google Sign‑In) |
| `LOGFIRE_API_KEY` | Logfire write token (optional) |
| `PORTKEY_API_KEY` | Portkey key (optional) |
| `PORTKEY_GROQ_PROVIDER` | Portkey provider slug, default `groq` (optional) |

---

## 6. Deploy

```bash
git push origin main
```

Watch **Repo → Actions**. The `test` job runs `pytest`; if it passes, `deploy`
builds both images, pushes them to Artifact Registry, and rolls them out to
Cloud Run. The final step prints the two URLs — the **retrieval** URL is your
storefront.

### First deploy is a three‑step dance

`cicd.yaml` deploys **ingestion** first (with `ALLOWED_ORIGINS=*`), reads its
URL, deploys **retrieval** with `INGESTION_SERVICE_URL` set to it, then goes
back and tightens ingestion's `ALLOWED_ORIGINS` to retrieval's real URL. This is
because Cloud Run only assigns a service its URL after the first deploy, and
each service needs to know the other's address. See
[`docs/07-deployment.md`](docs/07-deployment.md) for the reasoning.

---

## Redeploying / rolling back

Every deploy is a new Cloud Run **revision**. To roll back:

```bash
gcloud run revisions list --service=clothstore-retrieval --region=us-central1
gcloud run services update-traffic clothstore-retrieval \
  --region=us-central1 --to-revisions=REVISION_NAME=100
```

## Changing a setting without redeploying code

```bash
gcloud run services update clothstore-retrieval \
  --region=us-central1 \
  --update-env-vars "AGENT_MODEL_NAME=openai/gpt-oss-120b"
```
