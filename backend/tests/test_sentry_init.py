from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.config import DEFAULT_SENTRY_TRACES_SAMPLE_RATE, Settings, settings
from app.main import _init_sentry
from app.services import vector_store
from tests.conftest import TEST_NOTEBOOK_ID


def test_init_sentry_noop_without_dsn(monkeypatch: pytest.MonkeyPatch) -> None:
    """Bei leerem SENTRY_DSN (Standardfall, z.B. lokale Entwicklung/CI ohne Sentry-Account)
    darf sentry_sdk.init überhaupt nicht aufgerufen werden."""
    monkeypatch.setattr(settings, "sentry_dsn", "")
    mock_init = MagicMock()
    monkeypatch.setattr("sentry_sdk.init", mock_init)

    _init_sentry()

    mock_init.assert_not_called()


def test_init_sentry_called_with_dsn(monkeypatch: pytest.MonkeyPatch) -> None:
    """Bei gesetztem SENTRY_DSN muss sentry_sdk.init mit DSN, Environment und der
    FastAPI/Starlette-Integration aufgerufen werden."""
    monkeypatch.setattr(settings, "sentry_dsn", "https://examplekey@o0.ingest.sentry.io/1")
    monkeypatch.setattr(settings, "environment", "staging")
    mock_init = MagicMock()
    monkeypatch.setattr("sentry_sdk.init", mock_init)

    _init_sentry()

    mock_init.assert_called_once()
    _, kwargs = mock_init.call_args
    assert kwargs["dsn"] == "https://examplekey@o0.ingest.sentry.io/1"
    assert kwargs["environment"] == "staging"

    integration_types = {type(integration).__name__ for integration in kwargs["integrations"]}
    assert integration_types == {"StarletteIntegration", "FastApiIntegration"}


def test_init_sentry_passes_traces_sample_rate_from_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """traces_sample_rate muss unverändert aus settings.sentry_traces_sample_rate an
    sentry_sdk.init durchgereicht werden, damit die Kontingent-Konfiguration (siehe
    app/config.py) tatsächlich greift."""
    monkeypatch.setattr(settings, "sentry_dsn", "https://examplekey@o0.ingest.sentry.io/1")
    monkeypatch.setattr(settings, "sentry_traces_sample_rate", 0.2)
    mock_init = MagicMock()
    monkeypatch.setattr("sentry_sdk.init", mock_init)

    _init_sentry()

    mock_init.assert_called_once()
    _, kwargs = mock_init.call_args
    assert kwargs["traces_sample_rate"] == 0.2


def test_init_sentry_invalid_dsn_does_not_raise(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """Regression test for Bug 1: _init_sentry() läuft als bare Top-Level-Call beim
    Modul-Import von app/main.py, VOR `app = FastAPI(...)`. Ein ungültiger SENTRY_DSN
    (z.B. Tippfehler in einer Render-Env-Var) lässt sentry_sdk.init() eine BadDsn
    Exception werfen - würde diese nicht abgefangen, würde der komplette Import von
    app/main.py fehlschlagen und der Backend-Start vollständig scheitern, statt dass
    Sentry einfach nur inaktiv bleibt."""
    monkeypatch.setattr(settings, "sentry_dsn", "not-a-valid-dsn")
    monkeypatch.setattr(settings, "environment", "test")

    with caplog.at_level("WARNING"):
        _init_sentry()  # darf keine Exception werfen

    assert "Sentry" in caplog.text


@pytest.mark.parametrize("raw_value", ["", "not-a-number", "1.0abc", "None"])
def test_settings_invalid_sentry_traces_sample_rate_falls_back_to_default(
    monkeypatch: pytest.MonkeyPatch, raw_value: str
) -> None:
    """Regression test for Bug 3: Ein nicht-parsbarer SENTRY_TRACES_SAMPLE_RATE-Wert
    (z.B. ein versehentlich leer gelassenes Feld im Render-Dashboard) darf Settings()
    NICHT mit einer ValidationError abstürzen lassen -- das würde den kompletten
    Backend-Start verhindern (Settings() wird beim Modul-Import ausgeführt, lange bevor
    _init_sentry() via try/except abgesichert ist). Stattdessen muss auf den
    Standardwert zurückgefallen werden, analog zum Number.isFinite-Fallback in
    frontend/src/main.tsx."""
    monkeypatch.setenv("SENTRY_TRACES_SAMPLE_RATE", raw_value)

    test_settings = Settings()

    assert test_settings.sentry_traces_sample_rate == DEFAULT_SENTRY_TRACES_SAMPLE_RATE


@pytest.mark.parametrize("raw_value,expected", [("0.2", 0.2), ("5.0", 5.0), ("-1", -1.0)])
def test_settings_parsable_sentry_traces_sample_rate_is_used_unchanged(
    monkeypatch: pytest.MonkeyPatch, raw_value: str, expected: float
) -> None:
    """Werte außerhalb von [0, 1] sind zwar ungültig für Sentry, aber als Zahl parsbar --
    die werden bewusst unverändert durchgereicht. sentry_sdk validiert das intern
    (is_valid_sample_rate) und deaktiviert Sampling nur mit einer Warnung, statt zu
    crashen (separat verifiziert, hier nicht erneut geprüft)."""
    monkeypatch.setenv("SENTRY_TRACES_SAMPLE_RATE", raw_value)

    test_settings = Settings()

    assert test_settings.sentry_traces_sample_rate == expected


def test_unhandled_exception_reports_to_sentry(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Regression test for Bug 2: Sentrys ASGI-Hook liegt außerhalb der per
    app.add_middleware() registrierten Middlewares (siehe
    sentry_sdk/integrations/starlette.py, patch_asgi_app). Weil CatchAllExceptionsMiddleware
    Exceptions abfängt und nie erneut wirft, sieht Sentry sie strukturell nie - außer die
    Middleware ruft sentry_sdk.capture_exception() explizit selbst auf."""

    def raise_error(notebook_id: str) -> list[dict[str, str]]:
        raise RuntimeError("boom")

    monkeypatch.setattr(vector_store, "list_sources", raise_error)
    mock_capture_exception = MagicMock()
    monkeypatch.setattr("app.main.sentry_sdk.capture_exception", mock_capture_exception)

    response = client.get(f"/notebooks/{TEST_NOTEBOOK_ID}/sources")

    assert response.status_code == 500
    mock_capture_exception.assert_called_once()
