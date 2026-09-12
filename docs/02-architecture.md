# 2 · Architecture

## The big picture

```mermaid
flowchart TB
    U["🧑 Shopper's browser"]

    subgraph APP["LUXE application"]
        FE["Frontend<br/>(static JS + CSS)"]
        RE["Read endpoints<br/>list products, view cart,<br/>order history, chat"]
        WR["Write endpoints<br/>add to cart, place order,<br/>register, admin product CRUD"]
        BR["backend/ — shared code<br/>models · config · db · auth · utils · chatbot"]
    end

    DB[("MongoDB Atlas")]
    LLM["Groq<br/>(language models)"]
    LOG["Pydantic Logfire"]
    GID["Google Identity"]

    U <--> FE
    FE -->|GET requests| RE
    FE -->|POST/PUT/DELETE| WR
    RE --> BR
    WR --> BR
    BR <--> DB
    BR -->|chat / guardrails| LLM
    BR -.trace.-> LOG
    FE <-->|sign-in| GID
    BR -->|verify token| GID
```

Everything the shopper sees is the **frontend**. It only knows how to make small
JSON requests. All the logic lives in the **backend**, which is the only thing
that talks to the database and to Groq.

The backend's endpoints fall into two groups:

- **Reads** — anything that only *looks at* data: listing products, viewing one
  product, reading a cart, reading order history, and the chatbot (it only
  queries the database, it never changes it).
- **Writes** — anything that *changes* data: adding to a cart, placing an order,
  registering / logging in, editing a profile, and all the admin product
  operations.

Both groups are backed by the **same Python functions** in `backend/`. The
split is only about *which endpoints are mounted where* — see the next section.

## One entry point, reads and writes side by side

```mermaid
flowchart LR
    subgraph shared["backend/routes/*.py"]
        direction TB
        note["each module defines<br/>read_router + write_router"]
    end

    shared --> M["main.py<br/><b>Monolith</b><br/>mounts read + write<br/>+ serves the frontend<br/>→ one process, port 8000"]
```

```bash
python main.py
```

One FastAPI process on **port 8000** that serves the frontend *and* every API
endpoint, including the chatbot. The frontend asks the backend where to send
"write" requests (via a tiny `GET /config` endpoint); the monolith answers
"same place as everything else."

> New endpoints are added in one place: a decorator on `read_router` or
> `write_router` inside the relevant `backend/routes/*.py` module — `main.py`
> mounts both automatically.

## Identity — how the app knows who you are

LUXE keeps this deliberately simple. There are **no session tokens**.

```mermaid
flowchart TD
    A["Browser opens the site"] --> B{Logged in before?}
    B -->|No| C["Generate a random guest id<br/>guest_ab12cd@luxe.com<br/>save it in localStorage"]
    B -->|Yes| D["Use the saved email<br/>from localStorage"]
    C --> E["Every request carries this<br/>email as the identity"]
    D --> E
    E --> F["Cart / orders are stored<br/>against that email string"]
```

- A **guest** gets a random `guest_…@luxe.com` id stored in the browser. Their
  cart and orders are tied to that string.
- **Registering or signing in** replaces the guest id with a real email. From
  then on the cart and orders follow the real email.
- **Admin** actions send the user's email in an `X-User-Email` header; the
  backend checks an `is_admin` flag on that user's database document. This is a
  convenience gate for a demo, not a security boundary.

Passwords are hashed with **bcrypt** before storage. "Sign in with Google"
works differently: Google gives the browser a signed token, the backend
verifies Google's signature (using the `google-auth` library), and trusts the
email inside — no password involved.

## What happens on a request — three walkthroughs

### Loading the home page

```mermaid
sequenceDiagram
    participant B as Browser
    participant F as Frontend
    participant API as Backend
    participant DB as MongoDB

    B->>F: GET /  (index.html, main.js, style.css)
    F->>API: GET /config
    API-->>F: where to send writes
    F->>API: GET /auth/is-admin?email=(id)
    F->>API: GET /cart/(id)   (for the header count)
    F->>API: GET /products?cat=&min=&max=
    API->>DB: find products
    DB-->>API: matching documents
    API-->>F: product list (JSON)
    F->>B: render the grid
```

### Adding to the cart

```mermaid
sequenceDiagram
    participant B as Browser
    participant API as Backend
    participant DB as MongoDB

    B->>API: POST /cart/add {email, product_name, quantity}
    API->>DB: is this product already in the cart?
    alt already there
        API->>DB: increase its quantity
    else new
        API->>DB: insert a new cart row
    end
    API-->>B: {message: "Item added to cart"}
    B->>API: GET /cart/(id)   (refresh the header badge)
```

### Asking the assistant

See [AI Assistant](06-ai-assistant.md) for the full version. Short form:

```mermaid
sequenceDiagram
    participant B as Browser
    participant API as Backend
    participant G as Guardrails
    participant A as Agent
    participant DB as MongoDB

    B->>API: POST /chat {message}
    API->>G: is this message safe / not an attack?
    alt flagged
        API-->>B: polite refusal
    else ok
        API->>A: run the agent on the message
        A->>DB: search_products(filters)  (if it's a product query)
        DB-->>A: matches
        A-->>API: short confirmation text
        API->>G: is the reply safe?
        alt reply flagged
            API-->>B: polite refusal
        else ok
            API-->>B: {type: "products", message, data: [...]}
        end
    end
```
