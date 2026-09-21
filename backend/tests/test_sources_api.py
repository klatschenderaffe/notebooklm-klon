import io

import pytest
from fastapi.testclient import TestClient

import app.routers.sources as sources_router
from app.main import app
from app.services import storage, vector_store
from tests.conftest import TEST_NOTEBOOK_ID

BASE = f"/notebooks/{TEST_NOTEBOOK_ID}/sources"


def test_upload_source_rejects_unsupported_type(client: TestClient) -> None:
    response = client.post(
        BASE,
        files={"file": ("bild.png", io.BytesIO(b"data"), "image/png")},
    )
    assert response.status_code == 422


def test_upload_source_rejects_audio_file(client: TestClient) -> None:
    """Audio-Uploads wurden entfernt (früher via Gemini-Transkription unterstützt) —
    sie müssen jetzt wie jeder andere nicht unterstützte Dateityp klar abgelehnt werden,
    statt still transkribiert zu werden."""
    response = client.post(
        BASE,
        files={"file": ("aufnahme.wav", io.BytesIO(b"RIFF...fake-wav-bytes"), "audio/wav")},
    )
    assert response.status_code == 422


def test_upload_source_success(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        sources_router, "embed_texts", lambda chunks, task_type: [[0.1, 0.2] for _ in chunks]
    )
    monkeypatch.setattr(
        storage,
        "upload_source_file",
        lambda user_id, notebook_id, source_id, filename, content, file_type: (
            f"{user_id}/{notebook_id}/{source_id}/{filename}"
        ),
    )
    monkeypatch.setattr(
        vector_store,
        "insert_source",
        lambda source_id, notebook_id, filename, file_type, storage_path: {
            "id": source_id,
            "filename": filename,
            "file_type": file_type,
            "created_at": "2026-09-16T00:00:00Z",
        },
    )
    monkeypatch.setattr(vector_store, "insert_chunks", lambda source_id, chunks, embeddings: None)

    response = client.post(
        BASE,
        files={"file": ("notiz.md", io.BytesIO(b"# Titel\n\nInhalt"), "text/markdown")},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["filename"] == "notiz.md"
    assert body["file_type"] == "md"


def test_upload_source_cleans_up_on_chunk_insert_failure(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Regression test: found live when a bug in embed_texts made insert_chunks fail
    after the storage file and source row had already been created — leaving a
    zero-chunk "ghost" source that appeared normal in the UI but could never be found
    by chat. _ingest_source must roll back both on any failure after the storage
    upload.
    """
    monkeypatch.setattr(
        sources_router, "embed_texts", lambda chunks, task_type: [[0.1, 0.2] for _ in chunks]
    )
    monkeypatch.setattr(
        storage,
        "upload_source_file",
        lambda user_id, notebook_id, source_id, filename, content, file_type: (
            f"{user_id}/{notebook_id}/{source_id}/{filename}"
        ),
    )
    monkeypatch.setattr(
        vector_store,
        "insert_source",
        lambda source_id, notebook_id, filename, file_type, storage_path: {
            "id": source_id,
            "filename": filename,
            "file_type": file_type,
            "created_at": "2026-09-16T00:00:00Z",
        },
    )

    def failing_insert_chunks(source_id: str, chunks: list, embeddings: list) -> None:
        raise ValueError("zip() argument 2 is shorter than argument 1")

    monkeypatch.setattr(vector_store, "insert_chunks", failing_insert_chunks)

    deleted_storage_paths = []
    deleted_source_ids = []
    monkeypatch.setattr(
        storage, "delete_source_file", lambda path: deleted_storage_paths.append(path)
    )
    monkeypatch.setattr(
        vector_store,
        "delete_source",
        lambda notebook_id, source_id: deleted_source_ids.append(source_id),
    )

    response = client.post(
        BASE,
        files={"file": ("notiz.md", io.BytesIO(b"# Titel\n\nInhalt"), "text/markdown")},
    )

    assert response.status_code == 500
    assert len(deleted_storage_paths) == 1
    assert len(deleted_source_ids) == 1


def test_upload_source_rejects_invalid_encoding(client: TestClient) -> None:
    """Regression test: eine .md-Datei mit ungültigem UTF-8 muss als 422 mit klarer
    Meldung beantwortet werden, nicht als generischer 500 (siehe test_text_extraction.py
    für den Unit-Test der zugrunde liegenden ValueError)."""
    response = client.post(
        BASE,
        files={"file": ("notiz.md", io.BytesIO(b"\xff\xfe invalid"), "text/markdown")},
    )
    assert response.status_code == 422


def test_upload_source_rejects_empty_text(client: TestClient) -> None:
    response = client.post(
        BASE,
        files={"file": ("leer.md", io.BytesIO(b"   \n\n  "), "text/markdown")},
    )
    assert response.status_code == 422


def test_list_sources(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(vector_store, "list_sources", lambda notebook_id: [])
    response = client.get(BASE)
    assert response.status_code == 200
    assert response.json() == []


def test_delete_source_removes_storage_file(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        vector_store,
        "get_source",
        lambda notebook_id, source_id: {
            "id": source_id,
            "storage_path": f"user/{notebook_id}/{source_id}/notiz.md",
        },
    )
    removed_paths = []
    monkeypatch.setattr(storage, "delete_source_file", lambda path: removed_paths.append(path))
    monkeypatch.setattr(vector_store, "delete_source", lambda notebook_id, source_id: None)

    response = client.delete(f"{BASE}/some-source-id")

    assert response.status_code == 204
    assert removed_paths == [f"user/{TEST_NOTEBOOK_ID}/some-source-id/notiz.md"]


def test_delete_source_not_found(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(vector_store, "get_source", lambda notebook_id, source_id: None)
    response = client.delete(f"{BASE}/missing-id")
    assert response.status_code == 404


def test_sources_require_authentication() -> None:
    unauthenticated_client = TestClient(app)
    response = unauthenticated_client.get(BASE)
    assert response.status_code == 401


def _stub_ingest(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        sources_router, "embed_texts", lambda chunks, task_type: [[0.1, 0.2] for _ in chunks]
    )
    monkeypatch.setattr(
        storage,
        "upload_source_file",
        lambda user_id, notebook_id, source_id, filename, content, file_type: (
            f"{user_id}/{notebook_id}/{source_id}/{filename}"
        ),
    )
    monkeypatch.setattr(
        vector_store,
        "insert_source",
        lambda source_id, notebook_id, filename, file_type, storage_path: {
            "id": source_id,
            "filename": filename,
            "file_type": file_type,
            "created_at": "2026-09-16T00:00:00Z",
        },
    )
    monkeypatch.setattr(vector_store, "insert_chunks", lambda source_id, chunks, embeddings: None)


def test_add_url_source_success(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_ingest(monkeypatch)
    monkeypatch.setattr(
        sources_router,
        "extract_url_content",
        lambda url: ("Artikeltitel", "Der extrahierte Haupttext."),
    )

    response = client.post(f"{BASE}/url", json={"url": "https://example.org/artikel"})

    assert response.status_code == 201
    body = response.json()
    assert body["filename"] == "Artikeltitel"
    assert body["file_type"] == "url"


def test_add_url_source_extraction_failure_returns_422(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.services.web_extraction import UrlExtractionError

    def raise_error(url: str) -> tuple[str, str]:
        raise UrlExtractionError("Seite nicht erreichbar")

    monkeypatch.setattr(sources_router, "extract_url_content", raise_error)

    response = client.post(f"{BASE}/url", json={"url": "https://does-not-exist.invalid"})

    assert response.status_code == 422


