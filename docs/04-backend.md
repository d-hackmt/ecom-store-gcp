# 4 · Backend

The backend is a **FastAPI** (Python) application. Its job is to receive HTTP
requests from the frontend, do the work (talk to MongoDB, call the AI), and
return JSON.

## Package layout

```
backend/
  config.py        one typed Settings object; the only place .env is read
  database.py      the MongoDB connection + the four collection handles
  models.py        Pydantic models = the shape of each request body
  auth.py          the "is this user an admin?" check
  routes/          one module per area, each exposing read_router + write_router
    products.py        single-product CRUD
    products_bulk.py    JSON bulk-add + Excel/zip upload
    orders.py          place order, order history
    cart.py            add / list / clear cart
    chatbot.py         POST /chat  (thin HTTP layer — calls chatbot/pipeline.py; see doc 6)
    auth.py            is-admin, register, login
    google_auth.py     Google Sign-In
    profile.py         view/edit profile, avatar, delete account
  utils/
    images.py       upload → base64 helpers, and the "shape image for the API" helper
    mongo.py        small reusable query fragments (case-insensitive match)
    passwords.py    bcrypt hash / verify
    users.py        turn a user document into a safe public object (never leak the hash)
  chatbot/          the portable assistant package (kept in sync with the POC branch)
    agent.py        the Pydantic AI agent + its search_products tool
    guardrails.py   the two safety-model checks
    pipeline.py     run_chat(): guards -> agent -> guard -> response dict
    online_evals.py background quality scoring on live chats (toggled by a setting)
main.py            the monolith entry point — mounts every route module
```

## Route modules — reads and writes side by side

Every module in `backend/routes/` defines **two** routers:

```python
read_router  = APIRouter(prefix="/products", tags=["Products"])
write_router = APIRouter(prefix="/products", tags=["Products"])

@read_router.get("")            # GET /products
def get_products(...): ...

@write_router.post("")          # POST /products
async def add_product(...): ...
```

`main.py` (the monolith, and only entry point on this branch) mounts every
`read_router` **and** `write_router`, plus serves the frontend and `GET /config`.

## Every endpoint

### Products

| Method | Path | Auth | What it does |
|--------|------|------|--------------|
| `GET` | `/products` | – | List products. Optional `?category=`, `?min_price=`, `?max_price=`. |
| `GET` | `/products/{id}` | – | One product by id. `400` if the id is malformed, `404` if not found. |
| `POST` | `/products` | admin | Add a product. `multipart/form-data` (the image is uploaded and stored as base64). |
| `PUT` | `/products/{id}` | admin | Update a product. Also `multipart/form-data`; only the fields you send change. |
| `DELETE` | `/products/{id}` | admin | Delete one product. |
| `DELETE` | `/products` | admin | Delete **all** products. |
| `POST` | `/products/bulk` | admin | Add many products from a JSON array. |
| `POST` | `/products/bulk-upload` | admin | Add many products from an `.xlsx` sheet + a `.zip` of images. Bad rows are skipped and reported. |

### Cart & orders

| Method | Path | What it does |
|--------|------|--------------|
| `POST` | `/cart/add` | Add an item. If the product is already in the cart, its quantity is increased instead of adding a duplicate row. |
| `GET` | `/cart/{email}` | List a user's cart items. |
| `DELETE` | `/cart/{email}` | Empty a user's cart (used after checkout). |
| `POST` | `/orders` | Record an order (`{email, product_name, quantity, price}`), stamped with the time. |
| `GET` | `/orders/{email}` | A user's past orders, newest first. |

### Accounts

| Method | Path | What it does |
|--------|------|--------------|
| `GET` | `/auth/is-admin?email=` | Is this email an admin? (`{is_admin: true/false}`) |
| `POST` | `/auth/register` | Create an account (username, email, password ≥ 6 chars). |
| `POST` | `/auth/login` | Log in with email **or** username, plus password. |
| `POST` | `/auth/google` | Verify a Google ID token; auto‑registers a new email. |
| `GET` | `/auth/google-client-id` | The public Google client id, for the sign‑in button. |
| `GET` | `/auth/profile?email=` | A user's public profile (username, email, avatar). |
| `PUT` | `/auth/profile` | Edit username / email / password. Requires the current password. |
| `POST` | `/auth/avatar` | Upload a profile picture (stored as base64). |
| `DELETE` | `/auth/account` | Permanently delete the account and its cart. Requires the password. |

### Assistant & housekeeping

| Method | Path | What it does |
|--------|------|--------------|
| `POST` | `/chat` | Send a message, get back `{type: "text" \| "products", message, data}`. See [doc 6](06-ai-assistant.md). |
| `GET` | `/config` | Tells the frontend where to send write requests. |

## Configuration — one object

`backend/config.py` builds a single `settings` object with
[pydantic‑settings](08-glossary.md). Every environment variable the app reads is
declared there once, with a type and a default:

```python
from backend.config import settings
MongoClient(settings.mongo_uri)
```

`.env` is loaded in exactly this one file. See `.env.example` for the full list;
the important ones:

| Variable | Needed for |
|----------|-----------|
| `MONGO_URI` | the database connection |
| `GROQ_API_KEY` | every language‑model call |
| `GOOGLE_CLIENT_ID` | "Sign in with Google" |
| `LOGFIRE_API_KEY` | tracing (optional) |
| `PORTKEY_API_KEY`, `PORTKEY_GROQ_PROVIDER` | routing model calls through Portkey (optional) |

Anything left as a `REPLACE_WITH_…` placeholder is treated as "not set."

## Database module

`backend/database.py` creates the MongoDB client (which connects lazily — no
network call happens just by importing the module) and exposes four collection
handles: `users_collection`, `products_collection`, `orders_collection`,
`cart_collection`. On startup each FastAPI app calls `ensure_indexes()` once, in
a lifespan handler, to create the unique indexes on `users.email` and
`users.username`.

## Validation

Request bodies are Pydantic models (`backend/models.py`). FastAPI validates the
incoming JSON against them automatically and returns a `422` with a clear
message if it doesn't fit — so route functions can assume their input is the
right shape. Quantities must be ≥ 1, prices ≥ 0.

## Observability

`main.py` (and each service) calls `logfire.configure(...)` and then
`logfire.instrument_fastapi(app)`. From then on every request is a span in
[Pydantic Logfire](08-glossary.md), and the AI agent's runs are nested spans
inside the `/chat` request that triggered them. Errors in the chatbot are
recorded with `logfire.exception(...)`.
