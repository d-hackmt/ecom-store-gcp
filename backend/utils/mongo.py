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
