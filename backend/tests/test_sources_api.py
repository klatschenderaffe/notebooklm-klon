import io

import pytest
from fastapi.testclient import TestClient

import app.routers.sources as sources_router
from app.main import app
from app.services import storage, vector_store

client = TestClient(app)


def test_upload_source_rejects_unsupported_type() -> None:
    response = client.post(
        "/sources",
        files={"file": ("bild.png", io.BytesIO(b"data"), "image/png")},
    )
    assert response.status_code == 422


def test_upload_source_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        sources_router, "embed_texts", lambda chunks, task_type: [[0.1, 0.2] for _ in chunks]
    )
    monkeypatch.setattr(
        storage,
        "upload_source_file",
        lambda source_id, filename, content: f"{source_id}/{filename}",
    )
    monkeypatch.setattr(
        vector_store,
        "insert_source",
        lambda source_id, filename, file_type, storage_path: {
            "id": source_id,
            "filename": filename,
            "file_type": file_type,
            "created_at": "2026-09-16T00:00:00Z",
        },
    )
    monkeypatch.setattr(vector_store, "insert_chunks", lambda source_id, chunks, embeddings: None)

    response = client.post(
        "/sources",
        files={"file": ("notiz.md", io.BytesIO(b"# Titel\n\nInhalt"), "text/markdown")},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["filename"] == "notiz.md"
    assert body["file_type"] == "md"


def test_upload_source_rejects_empty_text() -> None:
    response = client.post(
        "/sources",
        files={"file": ("leer.md", io.BytesIO(b"   \n\n  "), "text/markdown")},
    )
    assert response.status_code == 422


def test_list_sources(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(vector_store, "list_sources", lambda: [])
    response = client.get("/sources")
    assert response.status_code == 200
    assert response.json() == []
