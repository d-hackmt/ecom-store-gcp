# 8 · Glossary

Every technical term used in these docs, one sentence each.

## The web app

| Term | Meaning |
|------|---------|
| **Frontend** | The code that runs in the shopper's browser — the pages, buttons and styling they see. |
| **Backend** | The code that runs on a server — it holds the data and the logic; the frontend can't see it directly. |
| **API** | The fixed list of requests the frontend is allowed to make to the backend (e.g. `GET /products`) and what each one returns. |
| **Endpoint / route** | One specific API address + method, e.g. `POST /cart/add`. |
| **HTTP request** | A message from the browser to the backend: a method (GET/POST/…), a path, optional headers, and an optional body. |
| **JSON** | A simple text format for structured data (`{"name": "Tee", "price": 799}`); the frontend and backend talk to each other in JSON. |
| **FastAPI** | The Python library that maps each incoming request to a Python function and turns the return value into JSON. |
| **Pydantic** | A Python library that describes the expected shape of data and rejects anything that doesn't fit. |
| **pydantic‑settings** | Pydantic's companion for configuration — one typed object holding every setting, read from environment variables. |
| **ES modules** | The browser's built‑in `import` / `export`; lets the frontend be many small `.js` files with no bundler. |
| **Hash routing** | Deciding what to show from the part of the URL after `#`, entirely in the browser, with no page reload. |
| **`localStorage`** | A small key‑value store the browser keeps per website; used here to remember the session email. |
| **DOM** | The live tree of elements that makes up the current page; JavaScript edits it to change what's on screen. |
| **`innerHTML`** | Setting an element's HTML content as a string; how each page here renders itself. |
| **Escaping** | Replacing characters like `<` and `"` with safe equivalents so text from the database can't inject markup. |
| **CORS** | A browser rule about which other websites' JavaScript may call this backend; configured with `ALLOWED_ORIGINS`. |

## Data

| Term | Meaning |
|------|---------|
| **MongoDB** | A database that stores records as flexible JSON‑like **documents** instead of fixed table rows. |
| **MongoDB Atlas** | MongoDB run for you in the cloud, managed through MongoDB's own dashboard. |
| **Collection** | MongoDB's version of a table — a group of documents (`users`, `products`, `orders`, `cart`). |
| **Document** | One record in a collection, shaped like a JSON object. |
| **`_id` / `ObjectId`** | The unique id MongoDB stamps on every document; the API converts it to a plain string called `id` before sending it out. |
| **Index** | A lookup structure MongoDB maintains for speed or uniqueness; here, unique indexes stop duplicate emails/usernames. |
| **base64** | A way to write binary data (like an image) as plain text so it can live inside a database document or a JSON response. |
| **bcrypt** | A one‑way password hashing function; the original password can't be recovered from the stored hash. |

## Deployment

| Term | Meaning |
|------|---------|
| **Docker** | Packages an app plus its dependencies into an **image** that runs the same on any machine. |
| **Image** | The packaged, ready‑to‑run snapshot of the app; a running copy of an image is a **container**. |
| **Uvicorn** | The program that actually serves a FastAPI app over HTTP. |
| **CI/CD** | Continuous Integration / Continuous Deployment — automation that tests and ships code on every push. |
| **Google Cloud Build** | Google Cloud's build automation service; this project's pipeline lives in `cloudbuild.yaml` and runs on every push to build the image and deploy it. |
| **Google Cloud Run** | A Google Cloud service that runs a container image on demand, gives it an HTTPS URL, and scales it (including to zero). |
| **Artifact Registry** | Google Cloud's private store for Docker images. |
| **Secret Manager** | Google Cloud's store for sensitive values (`MONGO_URI`, `GOOGLE_CLIENT_ID`); `cloudbuild.yaml` injects them into the container at deploy time. |
| **Service account** | A non‑human Google Cloud identity that automation acts as; it is granted specific roles. |
| **IAM** | Google Cloud's "who can do what" system — identities, roles and permissions. |

## Identity in this app

| Term | Meaning |
|------|---------|
| **Guest session** | An auto‑generated `guest_…@luxe.com` email stored in the browser for a visitor who hasn't signed in. |
| **`X-User-Email` header** | The header the frontend sends on admin requests so the backend can check the `is_admin` flag. |
| **Google Sign‑In** | Logging in with a Google account; Google gives the browser a signed token, the backend verifies the signature. |
| **ID token** | The signed proof‑of‑identity JWT that Google Sign‑In produces. |
