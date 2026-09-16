import pytest
from fastapi.testclient import TestClient

import app.routers.presentations as presentations_router
from app.main import app

client = TestClient(app)


def test_create_presentation_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        presentations_router.vector_store,
        "chunks_for_sources",
        lambda source_ids: [{"content": "Inhalt", "source_id": "1"}],
    )
    monkeypatch.setattr(
        presentations_router,
        "generate_presentation_outline",
        lambda topic, context_chunks: {
            "title": "Titel",
            "slides": [{"title": "Folie 1", "bullets": ["A", "B"]}],
        },
    )

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
