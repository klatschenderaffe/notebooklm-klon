from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

import app.services.notebooks_store as notebooks_store
from app.auth import get_current_user_id
from app.main import app
from app.rate_limit import limiter

TEST_USER_ID = "11111111-1111-1111-1111-111111111111"
TEST_NOTEBOOK_ID = "22222222-2222-2222-2222-222222222222"


@pytest.fixture(autouse=True)
def _reset_rate_limiter() -> None:
    """Der Rate-Limiter (app.rate_limit.limiter) hält seinen In-Memory-Zähler-Stand als
    Modul-globalen Zustand, der über die gesamte Testsession hinweg geteilt wird --
    ohne Reset würden sich POST-Requests aus VERSCHIEDENEN Testfunktionen gegenseitig
    ihr Kontingent wegnehmen (alle nicht-authentifizierten TestClient-Requests fallen
    im Rate-Limit-Key auf dieselbe Adresse zurück, siehe app/rate_limit.py), sodass
    Tests je nach Ausführungsreihenfolge/-anzahl unvorhersehbar mit 429 fehlschlagen
    könnten. autouse=True sorgt dafür, dass jede Testfunktion mit einem sauberen Stand
    startet; Tests, die das Rate-Limiting selbst prüfen (tests/test_rate_limit.py),
    lösen es innerhalb einer einzelnen Testfunktion trotzdem zuverlässig aus."""
    limiter.reset()


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    """Authentifizierter TestClient: überschreibt die Auth-Dependency (echte FastAPI-
    Dependency-Override) und mockt die Notebook-Eigentümerschaftsprüfung (normaler
    Funktionsaufruf, daher via monkeypatch statt dependency_overrides)."""
    app.dependency_overrides[get_current_user_id] = lambda: TEST_USER_ID
    monkeypatch.setattr(
        notebooks_store,
        "get_owned_notebook",
        lambda user_id, notebook_id: {"id": notebook_id, "user_id": user_id, "name": "Test"},
    )
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()
