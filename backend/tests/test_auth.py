from unittest.mock import MagicMock

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


def test_get_current_user_id_sets_sentry_user(monkeypatch: pytest.MonkeyPatch) -> None:
    """Bei erfolgreicher Token-Verifikation muss der Fehler-Report in Sentry der
    user_id zugeordnet werden - bewusst NUR die id, keine E-Mail/IP/sonstigen PII (siehe
    app/auth.py)."""
    monkeypatch.setattr(settings, "supabase_jwt_secret", "test-secret")
    mock_set_user = MagicMock()
    monkeypatch.setattr("app.auth.sentry_sdk.set_user", mock_set_user)
    token = jwt.encode(
        {"sub": "user-123", "aud": "authenticated"}, "test-secret", algorithm="HS256"
    )

    user_id = get_current_user_id(_make_request({"Authorization": f"Bearer {token}"}))

    assert user_id == "user-123"
    mock_set_user.assert_called_once_with({"id": "user-123"})


def test_get_current_user_id_does_not_set_sentry_user_on_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Bei fehlgeschlagener Token-Verifikation darf kein (nicht vertrauenswürdiger)
    Nutzer an Sentry gemeldet werden."""
    monkeypatch.setattr(settings, "supabase_jwt_secret", "test-secret")
    mock_set_user = MagicMock()
    monkeypatch.setattr("app.auth.sentry_sdk.set_user", mock_set_user)
    token = jwt.encode(
        {"sub": "user-123", "aud": "authenticated"}, "wrong-secret", algorithm="HS256"
    )

    with pytest.raises(HTTPException):
        get_current_user_id(_make_request({"Authorization": f"Bearer {token}"}))

    mock_set_user.assert_not_called()
