from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

import app.services.notebooks_store as notebooks_store
from app.auth import get_current_user_id
from app.main import app

TEST_USER_ID = "11111111-1111-1111-1111-111111111111"
TEST_NOTEBOOK_ID = "22222222-2222-2222-2222-222222222222"


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
