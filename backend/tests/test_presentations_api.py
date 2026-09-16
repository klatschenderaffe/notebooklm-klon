import pytest
from fastapi.testclient import TestClient

import app.routers.presentations as presentations_router
from app.main import app

client = TestClient(app)


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


def test_create_presentation_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        presentations_router.vector_store,
        "chunks_for_sources",
        lambda source_ids: [{"content": "Inhalt", "source_id": "1"}],
    )
    monkeypatch.setattr(presentations_router, "generate_presentation_outline", _fake_outline)

    response = client.post("/presentations", json={"topic": "Testthema"})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )
    assert len(response.content) > 0


def test_create_presentation_without_sources_returns_422(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        presentations_router.vector_store, "chunks_for_sources", lambda source_ids: []
    )
    response = client.post("/presentations", json={"topic": "Testthema"})
    assert response.status_code == 422
