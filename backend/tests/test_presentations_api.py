import pytest
from fastapi.testclient import TestClient

import app.routers.presentations as presentations_router
from tests.conftest import TEST_NOTEBOOK_ID

BASE = f"/notebooks/{TEST_NOTEBOOK_ID}/presentations"


def _fake_outline(
    topic: str,
    context_chunks: list[str],
    design_description: str | None = None,
    tone: str | None = None,
    slide_count_hint: str | None = None,
) -> dict:
    return {
        "title": "Titel",
        "design": {
            "background_color": "#FFFFFF",
            "accent_color": "#16A34A",
            "text_color": "#111111",
            "heading_font": "Calibri",
            "body_font": "Calibri",
        },
        "slides": [{"title": "Folie 1", "bullets": ["A", "B"]}],
    }


def _stub_persistence(monkeypatch: pytest.MonkeyPatch) -> dict:
    saved: dict = {}
    monkeypatch.setattr(
        presentations_router.storage,
        "upload_presentation_file",
        lambda user_id, notebook_id, presentation_id, content: "user/notebook/id.pptx",
    )
    monkeypatch.setattr(
        presentations_router.history_store,
        "insert_presentation",
        lambda notebook_id, title, topic, storage_path, design: saved.update(
            {"notebook_id": notebook_id, "title": title, "topic": topic}
        ),
    )
    return saved


def test_create_presentation_success(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        presentations_router.vector_store,
        "chunks_for_sources",
        lambda notebook_id, source_ids: [{"content": "Inhalt", "source_id": "1"}],
    )
    monkeypatch.setattr(presentations_router, "generate_presentation_outline", _fake_outline)
    saved = _stub_persistence(monkeypatch)

    response = client.post(BASE, json={"topic": "Testthema"})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )
    assert len(response.content) > 0
    assert saved["title"] == "Titel"
    assert saved["topic"] == "Testthema"


def test_create_presentation_without_sources_returns_422(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        presentations_router.vector_store, "chunks_for_sources", lambda notebook_id, source_ids: []
    )
    response = client.post(BASE, json={"topic": "Testthema"})
    assert response.status_code == 422


def test_list_presentations(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        presentations_router.history_store,
        "list_presentations",
        lambda notebook_id: [
            {
                "id": "1",
                "title": "Titel",
                "topic": "Thema",
                "created_at": "2026-09-17T00:00:00Z",
            }
        ],
    )
    response = client.get(BASE)
    assert response.status_code == 200
    assert response.json()[0]["title"] == "Titel"


def test_download_presentation(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        presentations_router.history_store,
        "get_presentation",
        lambda notebook_id, presentation_id: {
            "id": presentation_id,
            "title": "Titel",
            "storage_path": "user/notebook/id.pptx",
        },
    )
    monkeypatch.setattr(
        presentations_router.storage, "download_presentation_file", lambda path: b"pptx-bytes"
    )
    response = client.get(f"{BASE}/some-id/download")
    assert response.status_code == 200
    assert response.content == b"pptx-bytes"


def test_download_presentation_not_found(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        presentations_router.history_store,
        "get_presentation",
        lambda notebook_id, presentation_id: None,
    )
    response = client.get(f"{BASE}/missing-id/download")
    assert response.status_code == 404
