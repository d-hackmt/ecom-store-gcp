# Complete Step-by-Step Guide: Deploying to Google Cloud Run with CI/CD

This `commands.md` file provides an extremely detailed, foolproof guide to deploying your project on Google Cloud Platform (GCP) using **Cloud Run**, **Artifact Registry**, and **Cloud Build**. 

By the end of this guide, your code will automatically deploy every time you push to your GitHub/GitLab repository!

> Everything here is done through the **Google Cloud Console website** — no `gcloud`
> CLI. The only `gcloud` invocation lives *inside* `cloudbuild.yaml`, where Cloud
> Build runs it server-side during the deploy step; you never type it yourself.

---

## Phase 1: Setting up Your Google Cloud Account

Before anything else, you need a GCP account and a project.

### 1. Create a Google Account
If you don't have one, go to [accounts.google.com](https://accounts.google.com/signup) and create a standard Google Account.

### 2. Log into Google Cloud Console
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Sign in with your Google account.
3. Accept the Terms of Service.

### 3. Enable Billing (Required)
Google Cloud requires a billing account to deploy services, even if you are on the free tier.
1. Click on the **Navigation Menu** (hamburger icon, top left) > **Billing**.
2. Click **Link a billing account** or **Add Billing Account**.
3. Fill in your details (country, address, credit card). You will get a $300 free trial, and you won't be charged unless you manually upgrade later.

### 4. Create a New Project
1. In the top blue navigation bar, click on the **Project Dropdown** (it might say "Select a project").
2. Click **New Project** in the top right of the popup.
3. Name it something recognizable (e.g., `cloth-store-production`).
4. Click **Create**.
5. **Crucial:** Once created, click the Project Dropdown again and **select your new project**.

---

## Phase 2: Enabling APIs and Setting Up Storage

GCP services are disabled by default to save resources. We need to turn on the ones we need.

### 1. Enable Required APIs
1. At the top of the GCP console, use the Search Bar.
2. Search for **Cloud Build API** and click on it. Click **Enable**.
3. Search for **Artifact Registry API** and click on it. Click **Enable**.
4. Search for **Cloud Run Admin API** and click on it. Click **Enable**.
5. Search for **Secret Manager API** and click on it. Click **Enable**.

### 2. Create an Artifact Registry (To store your Docker images)
1. In the GCP Search Bar, type **Artifact Registry** and click it.
2. Click **+ CREATE REPOSITORY** at the top.
3. **Name:** `store-repo` (must match the repo name in `cloudbuild.yaml`)
4. **Format:** Docker
5. **Region:** `asia-south1` (Mumbai) — this must match your MongoDB Atlas cluster's region, so the app isn't paying a cross-continent round trip on every database call. *Remember this region, you will need it later.*
6. Scroll down and click **Create**.

### 3. Create Your Secrets (Secret Manager)

Sensitive config (`MONGO_URI`) and the Google client id are stored in Secret
Manager, not in any file. `cloudbuild.yaml` reads them at deploy time.

1. In the GCP Search Bar, type **Secret Manager** and click it.
2. Click **+ CREATE SECRET** at the top.
3. **Name:** `MONGO_URI`
4. **Secret value:** paste your full connection string
   (`mongodb+srv://user:password@cluster.../?appName=...`).
5. Leave the rest as default and click **Create Secret**.
6. Click **+ CREATE SECRET** again. **Name:** `GOOGLE_CLIENT_ID`,
   **Secret value:** your OAuth client id
   (`...apps.googleusercontent.com`). Click **Create Secret**.

*To change a value later (e.g. after rotating the DB password): open the secret,
click **+ NEW VERSION**, paste the new value, click **Add New Version**. The
`:latest` reference in `cloudbuild.yaml` picks it up on the next deploy.*

---

## Phase 3: The Configuration File

We need to tell Google Cloud how to build and deploy your application.
**This repo already has a working `cloudbuild.yaml` at the project root** —
you don't need to create one. It looks like this:

```yaml
# Replace `store-repo` with your Artifact Registry repo name and `store` with
# your desired Cloud Run service name if you chose different ones above.

steps:
  # 1. Build the Docker image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'asia-south1-docker.pkg.dev/$PROJECT_ID/store-repo/main-app:$COMMIT_SHA', '.']

  # 2. Push the image to Artifact Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'asia-south1-docker.pkg.dev/$PROJECT_ID/store-repo/main-app:$COMMIT_SHA']

  # 3. Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'store'
      - '--image'
      - 'asia-south1-docker.pkg.dev/$PROJECT_ID/store-repo/main-app:$COMMIT_SHA'
      - '--region'
      - 'asia-south1'
      - '--allow-unauthenticated'
      - '--port'
      - '8000' # Change this if your app runs on a different port internally!
      - '--set-secrets'
      - 'MONGO_URI=MONGO_URI:latest,GOOGLE_CLIENT_ID=GOOGLE_CLIENT_ID:latest'

images:
  - 'asia-south1-docker.pkg.dev/$PROJECT_ID/store-repo/main-app:$COMMIT_SHA'

options:
  logging: CLOUD_LOGGING_ONLY
```

The `--set-secrets` line maps the Secret Manager secrets you created in Phase 2
into the container as environment variables (`MONGO_URI`, `GOOGLE_CLIENT_ID`).
Only edit this file if you deliberately want to change the region, service
name, or repo name — and if you do, make sure your Artifact Registry
repository (Phase 2) is created in the **same region** you put here.

### If you do change it, push the change
```bash
git add cloudbuild.yaml
git commit -m "Update Cloud Build configuration"
git push origin 01-store-only
```

---

## Phase 4: Granting Permissions (IAM)

This is the most common place where beginners get stuck. Cloud Build acts like an automated robot, and that robot needs permission to push files to the Artifact Registry and run the deployment.

### 1. Find Your Cloud Build Service Account
1. In the GCP Console, search for **IAM** in the top bar and click **IAM**.
2. Look through the list of "Principals" for an email address that ends in `@cloudbuild.gserviceaccount.com` OR has the name **Compute Engine default service account** (ending in `@developer.gserviceaccount.com`).
3. Click the **Pencil Icon (Edit Principal)** on the right side of that row.

### 2. Add Required Roles
1. In the Edit window, click **+ ADD ANOTHER ROLE**.
2. Search for and select **Cloud Run Admin**.
3. Click **+ ADD ANOTHER ROLE** again.
4. Search for and select **Artifact Registry Writer**.
5. Click **+ ADD ANOTHER ROLE** again.
6. Search for and select **Service Account User**.
7. Click **+ ADD ANOTHER ROLE** again.
8. Search for and select **Logs Writer**.
9. Click **+ ADD ANOTHER ROLE** again.
10. Search for and select **Secret Manager Secret Accessor** (lets the deployed service read `MONGO_URI` and `GOOGLE_CLIENT_ID`).
11. Click **Save**.

---

## Phase 5: Setting Up the Automation (The Trigger)

Now we connect your GitHub/GitLab repository to GCP so that pushing code automatically starts the deployment.

### 1. Connect Your Repository
1. In the GCP Search Bar, type **Cloud Build** and select it.
2. On the left sidebar, click **Triggers**.
3. Click **+ CREATE TRIGGER** at the top.

### 2. Configure the Trigger
1. **Name:** `cloth-store-pipeline`
2. **Event:** Choose "Push to a branch"
3. **Source:** 
   - Click the dropdown and select **Connect new repository**.
   - Select your provider (GitHub or GitLab).
   - Authenticate and authorize Google Cloud.
   - Select your specific repository (e.g., `Aanand2204/AI-Cloth-Store`).
4. **Branch:** type `^01-store-only$` (this means it will only trigger when you push to the `01-store-only` branch — change it if you're deploying a different branch).
5. **Configuration:** Select **Cloud Build configuration file (yaml or json)**.
6. **Location:** Type `cloudbuild.yaml`.
7. **Service Account:** Select the service account.
8. Click **Create** at the bottom.

---

## Phase 6: Running the Deployment

### 1. The Initial Run
1. Still on the **Triggers** page, find your newly created `cloth-store-pipeline`.
2. Click the **RUN** button on the far right.
3. On the left sidebar, click **History**.
4. Click on the build that is currently running to watch the live terminal output. 
5. Wait for all steps to turn green. (This may take 3-10 minutes).

*(Note: In the future, you do not need to click RUN. Just pushing code to your repository will automatically start this process!)*

---

## Phase 7: Post-Deployment Essentials

If your build succeeds but your website shows a "Service Unavailable" or crashes, it's usually because config is missing or wrong.

### 1. Config comes from Secret Manager

`cloudbuild.yaml` already injects `MONGO_URI` and `GOOGLE_CLIENT_ID` from the
secrets you created in Phase 2 (the `--set-secrets` line). You do **not** add
them by hand on the Cloud Run service.

If a value is wrong or you rotated the DB password:

1. In the GCP Search bar, type **Secret Manager** and click it.
2. Click the secret (e.g. `MONGO_URI`) → **+ NEW VERSION** → paste the new value → **Add New Version**.
3. Re-run the trigger (Phase 6) so a new revision picks up `:latest`.

To confirm what a running revision sees: **Cloud Run** → service `store` →
**Revisions** tab → select the revision → **Variables & Secrets**.

### 2. Get Your Live URL
Once the deployment finishes, look at the top of the Cloud Run service page. You will see a URL that looks like `https://store-xxxxx-uc.a.run.app`.

**Click it! Your application is now live on the internet!**
