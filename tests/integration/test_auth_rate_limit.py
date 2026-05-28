from fastapi.testclient import TestClient

from src.main import InMemoryRateLimiter, app


def _set_app_state(**values):
    previous = {}
    missing = object()
    for key, value in values.items():
        previous[key] = getattr(app.state, key, missing)
        setattr(app.state, key, value)
    return previous, missing


def _restore_app_state(previous, missing):
    for key, value in previous.items():
        if value is missing:
            try:
                delattr(app.state, key)
            except AttributeError:
                pass
        else:
            setattr(app.state, key, value)


def test_health_is_not_protected_by_api_key():
    previous, missing = _set_app_state(
        api_auth_enabled=True,
        api_key="secret",
        rate_limit_enabled=True,
        rate_limiter=InMemoryRateLimiter(limit=1, window_seconds=60),
    )
    try:
        response = TestClient(app).get("/health")
    finally:
        _restore_app_state(previous, missing)

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_query_rejects_missing_or_wrong_api_key_without_leaking_expected_secret():
    previous, missing = _set_app_state(
        api_auth_enabled=True,
        api_key="expected-secret",
        rate_limit_enabled=False,
    )
    client = TestClient(app)
    try:
        missing_key = client.post("/api/v1/query", json={})
        wrong_key = client.post(
            "/api/v1/query",
            headers={"X-API-Key": "wrong-secret"},
            json={},
        )
    finally:
        _restore_app_state(previous, missing)

    assert missing_key.status_code == 401
    assert wrong_key.status_code == 401
    assert missing_key.json() == {"detail": "Invalid or missing API key."}
    assert "expected-secret" not in missing_key.text
    assert "expected-secret" not in wrong_key.text


def test_query_accepts_valid_api_key_and_reaches_request_validation():
    previous, missing = _set_app_state(
        api_auth_enabled=True,
        api_key="expected-secret",
        rate_limit_enabled=False,
    )
    try:
        response = TestClient(app).post(
            "/api/v1/query",
            headers={"X-API-Key": "expected-secret"},
            json={},
        )
    finally:
        _restore_app_state(previous, missing)

    assert response.status_code == 422


def test_query_rate_limit_is_in_memory_and_key_scoped():
    previous, missing = _set_app_state(
        api_auth_enabled=True,
        api_key="expected-secret",
        rate_limit_enabled=True,
        rate_limiter=InMemoryRateLimiter(limit=2, window_seconds=60),
    )
    client = TestClient(app)
    headers = {"X-API-Key": "expected-secret"}
    try:
        first = client.post("/api/v1/query", headers=headers, json={})
        second = client.post("/api/v1/query", headers=headers, json={})
        third = client.post("/api/v1/query", headers=headers, json={})
    finally:
        _restore_app_state(previous, missing)

    assert first.status_code == 422
    assert second.status_code == 422
    assert third.status_code == 429
    assert third.json() == {"detail": "Rate limit exceeded."}


def test_rate_limiter_resets_after_window_with_injected_clock():
    now = [100.0]
    limiter = InMemoryRateLimiter(limit=1, window_seconds=10, clock=lambda: now[0])

    assert limiter.allow("client") is True
    assert limiter.allow("client") is False

    now[0] += 11

    assert limiter.allow("client") is True
