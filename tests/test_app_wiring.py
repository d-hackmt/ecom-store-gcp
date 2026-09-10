"""
Smoke test: every router is actually registered on the app. Catches a
forgotten `app.include_router(...)` in main.py without needing to know
every route's business logic.
"""
import main


def test_expected_route_prefixes_are_registered():
    schema = main.app.openapi()
    paths = schema["paths"].keys()

    expected_prefixes = ["/products", "/orders", "/cart", "/chat", "/auth"]
    for prefix in expected_prefixes:
        assert any(p.startswith(prefix) for p in paths), f"No routes registered under {prefix}"


def test_bulk_and_profile_routes_present():
    schema = main.app.openapi()
    paths = schema["paths"].keys()

    for expected_path in [
        "/products/bulk",
        "/products/bulk-upload",
        "/auth/register",
        "/auth/login",
        "/auth/profile",
        "/auth/avatar",
        "/auth/account",
        "/auth/google",
    ]:
        assert expected_path in paths, f"Missing route: {expected_path}"
