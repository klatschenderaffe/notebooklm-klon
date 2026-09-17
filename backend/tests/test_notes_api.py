import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import notes_store, vector_store
from tests.conftest import TEST_NOTEBOOK_ID

SOURCE_ID = "33333333-3333-3333-3333-333333333333"
BASE = f"/notebooks/{TEST_NOTEBOOK_ID}/sources/{SOURCE_ID}/notes"


def _stub_owned_source(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        vector_store,
        "get_source",
        lambda notebook_id, source_id: {"id": source_id, "notebook_id": notebook_id},
    )


def test_list_notes(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_owned_source(monkeypatch)
    monkeypatch.setattr(
        notes_store,
        "list_notes",
        lambda source_id: [{"id": "n1", "content": "Notiz", "created_at": "2026-09-17T00:00:00Z"}],
    )

    response = client.get(BASE)

    assert response.status_code == 200
    assert response.json() == [
        {"id": "n1", "content": "Notiz", "created_at": "2026-09-17T00:00:00Z"}
    ]


def test_list_notes_for_missing_source_returns_404(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(vector_store, "get_source", lambda notebook_id, source_id: None)

    response = client.get(BASE)

    assert response.status_code == 404


def test_add_note_success(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_owned_source(monkeypatch)
    monkeypatch.setattr(
        notes_store,
        "insert_note",
        lambda source_id, content: {
            "id": "n1",
            "content": content,
            "created_at": "2026-09-17T00:00:00Z",
        },
    )

    response = client.post(BASE, json={"content": "Wichtiger Punkt"})

    assert response.status_code == 201
    assert response.json()["content"] == "Wichtiger Punkt"


def test_add_note_rejects_empty_content(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _stub_owned_source(monkeypatch)

    response = client.post(BASE, json={"content": "   "})

    assert response.status_code == 422


def test_delete_note_success(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_owned_source(monkeypatch)
    monkeypatch.setattr(notes_store, "delete_note", lambda source_id, note_id: True)

    response = client.delete(f"{BASE}/n1")

    assert response.status_code == 204


def test_delete_note_not_found(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_owned_source(monkeypatch)
    monkeypatch.setattr(notes_store, "delete_note", lambda source_id, note_id: False)

    response = client.delete(f"{BASE}/missing")

    assert response.status_code == 404


def test_notes_require_authentication() -> None:
    unauthenticated_client = TestClient(app)
    response = unauthenticated_client.get(BASE)
    assert response.status_code == 401
