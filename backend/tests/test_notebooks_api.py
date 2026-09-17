import pytest
from fastapi.testclient import TestClient

import app.routers.notebooks as notebooks_router
from app.main import app
from tests.conftest import TEST_USER_ID


def test_list_notebooks(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        notebooks_router.notebooks_store,
        "list_notebooks",
        lambda user_id: [
            {"id": "1", "name": "Mein Notebook", "created_at": "2026-09-16T00:00:00Z"}
        ],
    )
    response = client.get("/notebooks")
    assert response.status_code == 200
    assert response.json()[0]["name"] == "Mein Notebook"


def test_create_notebook(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        notebooks_router.notebooks_store,
        "create_notebook",
        lambda user_id, name: {"id": "1", "name": name, "created_at": "2026-09-16T00:00:00Z"},
    )
    response = client.post("/notebooks", json={"name": "Neues Notebook"})
    assert response.status_code == 201
    assert response.json()["name"] == "Neues Notebook"


def test_notebooks_require_authentication() -> None:
    unauthenticated_client = TestClient(app)
    response = unauthenticated_client.get("/notebooks")
    assert response.status_code == 401


def test_delete_notebook_cleans_up_storage(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    removed_source_paths = []
    removed_presentation_paths = []
    monkeypatch.setattr(
        notebooks_router.notebooks_store,
        "list_source_storage_paths",
        lambda notebook_id: ["a/b/c/datei.pdf", "a/b/d/notiz.md"],
    )
    monkeypatch.setattr(
        notebooks_router.notebooks_store,
        "list_presentation_storage_paths",
        lambda notebook_id: ["a/b/praesentation.pptx"],
    )
    monkeypatch.setattr(
        notebooks_router.storage,
        "delete_source_file",
        lambda path: removed_source_paths.append(path),
    )
    monkeypatch.setattr(
        notebooks_router.storage,
        "delete_presentation_file",
        lambda path: removed_presentation_paths.append(path),
    )
    monkeypatch.setattr(
        notebooks_router.notebooks_store, "delete_notebook", lambda user_id, notebook_id: None
    )

    response = client.delete("/notebooks/some-notebook-id")

    assert response.status_code == 204
    assert removed_source_paths == ["a/b/c/datei.pdf", "a/b/d/notiz.md"]
    assert removed_presentation_paths == ["a/b/praesentation.pptx"]


def test_notebook_ownership_check_uses_current_user(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen_user_ids = []

    def fake_list_notebooks(user_id: str) -> list[dict]:
        seen_user_ids.append(user_id)
        return []

    monkeypatch.setattr(notebooks_router.notebooks_store, "list_notebooks", fake_list_notebooks)
    client.get("/notebooks")
    assert seen_user_ids == [TEST_USER_ID]
