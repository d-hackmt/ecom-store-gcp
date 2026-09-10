# Product schema (shared by the client)

The POC connects to the client's MongoDB Atlas cluster, database `ecommerce_db`,
and reads one collection: **`products`**. It never writes.

## A product document

```json
{
  "_id": "ObjectId(...)",
  "name": "Classic Black Tee",
  "description": "Soft combed-cotton crew neck",
  "price": 799,
  "category": "men",
  "size":  ["S", "M", "L", "XL"],
  "color": ["Black"],
  "image_data": "/9j/4AAQSkZJRg...",
  "image_content_type": "image/jpeg"
}
```

| Field | Type | Notes |
|-------|------|-------|
| `name` | string | |
| `description` | string | |
| `price` | int | rupees |
| `category` | string | one of `men`, `women`, `kids` |
| `size` | array of string | may be absent |
| `color` | array of string | may be absent |
| `image_data` + `image_content_type` | string | base64 image, for admin-uploaded photos |
| `image` | string | a plain URL instead, for products added via bulk JSON import |

## How the POC uses it

`search_products` builds a MongoDB query from the tool arguments:

| Tool argument | Query fragment |
|---------------|----------------|
| `category` | case-insensitive exact match on `category` |
| `keyword` | case-insensitive substring match on `name` |
| `min_price` / `max_price` | range on `price` |

It returns at most 8 matches. Before returning, each document's `_id` becomes a
string `id`, and the image is normalised to a single `image` field (the URL, or
a reconstructed `data:` URL) — the raw base64 fields are stripped.
