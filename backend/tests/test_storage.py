from typing import Any

import pytest

import app.services.storage as storage_module


class _FakeBucket:
    def __init__(self) -> None:
        self.calls: list[tuple[str, bytes, dict[str, Any]]] = []

    def upload(self, path: str, content: bytes, file_options: dict[str, Any]) -> None:
        self.calls.append((path, content, file_options))


class _FakeStorage:
    def __init__(self, bucket: _FakeBucket) -> None:
        self._bucket = bucket

    def from_(self, name: str) -> _FakeBucket:
        return self._bucket


class _FakeClient:
    def __init__(self, bucket: _FakeBucket) -> None:
        self.storage = _FakeStorage(bucket)


def test_upload_source_file_sets_explicit_pdf_content_type(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bucket = _FakeBucket()
    monkeypatch.setattr(storage_module, "get_client", lambda: _FakeClient(bucket))

    storage_module.upload_source_file("source-1", "dokument.pdf", b"%PDF-1.4", "pdf")

    [(path, content, file_options)] = bucket.calls
    assert path == "source-1/dokument.pdf"
    assert content == b"%PDF-1.4"
    assert file_options == {"content-type": "application/pdf"}


def test_upload_source_file_sets_explicit_markdown_content_type(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bucket = _FakeBucket()
    monkeypatch.setattr(storage_module, "get_client", lambda: _FakeClient(bucket))

    storage_module.upload_source_file("source-2", "notiz.md", b"# Titel", "md")

    [(_, _, file_options)] = bucket.calls
    assert file_options == {"content-type": "text/markdown"}
