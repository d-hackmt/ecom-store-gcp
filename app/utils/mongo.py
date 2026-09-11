"""
Shared MongoDB query-fragment helpers.
"""
import re


def case_insensitive_exact(value: str) -> dict:
    """Query fragment for an exact, case-insensitive string match."""
    return {"$regex": f"^{re.escape(value)}$", "$options": "i"}


def case_insensitive_contains(value: str) -> dict:
    """Query fragment for a case-insensitive substring match."""
    return {"$regex": re.escape(value), "$options": "i"}


def price_range_filter(min_price: int = None, max_price: int = None) -> dict:
    """Query fragment for a price range; empty dict if neither bound is given."""
    price_query = {}
    if min_price is not None:
        price_query["$gte"] = min_price
    if max_price is not None:
        price_query["$lte"] = max_price
    return price_query
