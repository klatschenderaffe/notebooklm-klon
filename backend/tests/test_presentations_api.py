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


def test_create_presentation_success(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        presentations_router.vector_store,
        "chunks_for_sources",
        lambda notebook_id, source_ids: [{"content": "Inhalt", "source_id": "1"}],
    )
    monkeypatch.setattr(presentations_router, "generate_presentation_outline", _fake_outline)

    response = client.post(BASE, json={"topic": "Testthema"})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )
    assert len(response.content) > 0


def test_create_presentation_without_sources_returns_422(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        presentations_router.vector_store, "chunks_for_sources", lambda notebook_id, source_ids: []
    )
    response = client.post(BASE, json={"topic": "Testthema"})
    assert response.status_code == 422
