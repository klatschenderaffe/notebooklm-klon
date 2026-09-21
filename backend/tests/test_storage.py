from typing import Any

import httpx
import pytest
from fastapi import HTTPException

import app.services.storage as storage_module


class _FakeBucket:
    def __init__(self) -> None:
        self.upload_calls: list[tuple[str, bytes, dict[str, Any]]] = []
        self.removed_paths: list[list[str]] = []

    def upload(self, path: str, content: bytes, file_options: dict[str, Any]) -> None:
        self.upload_calls.append((path, content, file_options))

    def remove(self, paths: list[str]) -> None:
        self.removed_paths.append(paths)


class _FakeStorage:
    def __init__(self, bucket: _FakeBucket) -> None:
        self._bucket = bucket

    def from_(self, name: str) -> _FakeBucket:
        return self._bucket


class _FakeClient:
    def __init__(self, bucket: _FakeBucket) -> None:
        self.storage = _FakeStorage(bucket)


def test_upload_source_file_uses_user_notebook_source_path_and_pdf_content_type(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bucket = _FakeBucket()
    monkeypatch.setattr(storage_module, "get_client", lambda: _FakeClient(bucket))

    storage_module.upload_source_file(
        "user-1", "notebook-1", "source-1", "dokument.pdf", b"%PDF-1.4", "pdf"
    )

    [(path, content, file_options)] = bucket.upload_calls
    assert path == "user-1/notebook-1/source-1/dokument.pdf"
    assert content == b"%PDF-1.4"
    assert file_options == {"content-type": "application/pdf"}


def test_upload_source_file_sets_explicit_markdown_content_type(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bucket = _FakeBucket()
    monkeypatch.setattr(storage_module, "get_client", lambda: _FakeClient(bucket))

    storage_module.upload_source_file(
        "user-1", "notebook-1", "source-2", "notiz.md", b"# Titel", "md"
    )

    [(_, _, file_options)] = bucket.upload_calls
    assert file_options == {"content-type": "text/markdown"}


def test_upload_source_file_sets_content_type_for_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bucket = _FakeBucket()
    monkeypatch.setattr(storage_module, "get_client", lambda: _FakeClient(bucket))

    storage_module.upload_source_file(
        "user-1", "notebook-1", "source-3", "Artikel.md", b"Text", "url"
    )

    assert bucket.upload_calls[0][2] == {"content-type": "text/markdown"}


@pytest.mark.parametrize(
    ("malicious_filename", "expected"),
    [
        ("../../../etc/passwd", "passwd"),
        ("..\\..\\..\\windows\\win.ini", "win.ini"),
        ("/etc/passwd", "passwd"),
        ("....//....//etc/passwd", "passwd"),
        ("...", "datei"),
        ("..", "datei"),
        (".hidden", "hidden"),
        ("   ", "datei"),
        ("..   ", "datei"),
    ],
)
def test_upload_source_file_sanitizes_path_traversal_filenames(
    monkeypatch: pytest.MonkeyPatch, malicious_filename: str, expected: str
) -> None:
    bucket = _FakeBucket()
    monkeypatch.setattr(storage_module, "get_client", lambda: _FakeClient(bucket))

    storage_module.upload_source_file(
        "user-1", "notebook-1", "source-1", malicious_filename, b"data", "md"
    )

    [(path, _content, _file_options)] = bucket.upload_calls
    assert path == f"user-1/notebook-1/source-1/{expected}"
    assert "/etc/" not in path
    assert ".." not in path


def test_upload_source_file_replaces_invalid_storage_key_characters(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Regression test: live in Sentry gefunden -- ein URL-Quellen-Titel wie
    "[Hiring] DevOps Engineer @Everlast..." ist kein Pfad-Traversal-Versuch, aber "[",
    "]" und "@" sind trotzdem keine gültigen Supabase-Storage-Key-Zeichen und ließen den
    Upload mit "Invalid key" fehlschlagen."""
    bucket = _FakeBucket()
    monkeypatch.setattr(storage_module, "get_client", lambda: _FakeClient(bucket))

    storage_module.upload_source_file(
        "user-1",
        "notebook-1",
        "source-1",
        "[Hiring] DevOps Engineer @Everlast Consulting GmbH",
        b"data",
        "md",
    )

    [(path, _content, _file_options)] = bucket.upload_calls
    assert path == ("user-1/notebook-1/source-1/_Hiring_ DevOps Engineer _Everlast Consulting GmbH")
    assert "[" not in path
    assert "]" not in path
    assert "@" not in path


class _OnceTimingOutThenSucceedingBucket(_FakeBucket):
    """Simuliert den live gefundenen Fall: der erste Upload-Versuch zur echten
    Supabase-Storage-API läuft nach dem 20s-Standard-Timeout der Bibliothek in ein
    httpx.ReadTimeout, der zweite Versuch (Sekunden später) läuft normal durch."""

    def __init__(self) -> None:
        super().__init__()
        self.call_count = 0

    def upload(self, path: str, content: bytes, file_options: dict[str, Any]) -> None:
        self.call_count += 1
        if self.call_count == 1:
            raise httpx.ReadTimeout("Zeitüberschreitung")
        super().upload(path, content, file_options)


def test_upload_source_file_retries_once_on_timeout_then_succeeds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(storage_module.time, "sleep", lambda _seconds: None)
    bucket = _OnceTimingOutThenSucceedingBucket()
    monkeypatch.setattr(storage_module, "get_client", lambda: _FakeClient(bucket))

    storage_path = storage_module.upload_source_file(
        "user-1", "notebook-1", "source-1", "dokument.pdf", b"%PDF-1.4", "pdf"
    )

    assert storage_path == "user-1/notebook-1/source-1/dokument.pdf"
    assert bucket.call_count == 2
    assert len(bucket.upload_calls) == 1


class _AlwaysTimingOutBucket(_FakeBucket):
    def __init__(self) -> None:
        super().__init__()
        self.call_count = 0

    def upload(self, path: str, content: bytes, file_options: dict[str, Any]) -> None:
        self.call_count += 1
        raise httpx.ReadTimeout("Zeitüberschreitung")


def test_upload_source_file_raises_503_when_timeout_persists(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Hält das Timeout auch beim zweiten Versuch an, muss sauber als 503 beim Nutzer
    ankommen, statt ungefangen als generischer 500 durchzuschlagen (live gefunden:
    genau das passierte, bevor diese Absicherung existierte)."""
    monkeypatch.setattr(storage_module.time, "sleep", lambda _seconds: None)
    bucket = _AlwaysTimingOutBucket()
    monkeypatch.setattr(storage_module, "get_client", lambda: _FakeClient(bucket))

    with pytest.raises(HTTPException) as exc_info:
        storage_module.upload_source_file(
            "user-1", "notebook-1", "source-1", "dokument.pdf", b"%PDF-1.4", "pdf"
        )

    assert exc_info.value.status_code == 503
    assert bucket.call_count == 2


def test_delete_source_file_removes_by_path(monkeypatch: pytest.MonkeyPatch) -> None:
    bucket = _FakeBucket()
    monkeypatch.setattr(storage_module, "get_client", lambda: _FakeClient(bucket))

    storage_module.delete_source_file("user-1/notebook-1/source-1/dokument.pdf")

    assert bucket.removed_paths == [["user-1/notebook-1/source-1/dokument.pdf"]]
