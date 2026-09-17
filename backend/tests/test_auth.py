import jwt
import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.auth import get_current_user_id
from app.config import settings


def _make_request(headers: dict[str, str]) -> Request:
    scope = {
        "type": "http",
        "headers": [(k.lower().encode(), v.encode()) for k, v in headers.items()],
    }
    return Request(scope)


def test_get_current_user_id_rejects_missing_header() -> None:
    with pytest.raises(HTTPException) as exc_info:
        get_current_user_id(_make_request({}))
    assert exc_info.value.status_code == 401


def test_get_current_user_id_rejects_malformed_header() -> None:
    with pytest.raises(HTTPException) as exc_info:
        get_current_user_id(_make_request({"Authorization": "NotBearer xyz"}))
    assert exc_info.value.status_code == 401


def test_get_current_user_id_accepts_valid_hs256_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "supabase_jwt_secret", "test-secret")
    token = jwt.encode(
        {"sub": "user-123", "aud": "authenticated"}, "test-secret", algorithm="HS256"
    )
    user_id = get_current_user_id(_make_request({"Authorization": f"Bearer {token}"}))
    assert user_id == "user-123"


def test_get_current_user_id_rejects_wrong_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "supabase_jwt_secret", "test-secret")
    token = jwt.encode(
        {"sub": "user-123", "aud": "authenticated"}, "wrong-secret", algorithm="HS256"
    )
    with pytest.raises(HTTPException) as exc_info:
        get_current_user_id(_make_request({"Authorization": f"Bearer {token}"}))
    assert exc_info.value.status_code == 401


def test_get_current_user_id_rejects_wrong_audience(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "supabase_jwt_secret", "test-secret")
    token = jwt.encode({"sub": "user-123", "aud": "other"}, "test-secret", algorithm="HS256")
    with pytest.raises(HTTPException) as exc_info:
        get_current_user_id(_make_request({"Authorization": f"Bearer {token}"}))
    assert exc_info.value.status_code == 401
