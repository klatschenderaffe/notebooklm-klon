from typing import Any

import pytest

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


def test_delete_source_file_removes_by_path(monkeypatch: pytest.MonkeyPatch) -> None:
    bucket = _FakeBucket()
    monkeypatch.setattr(storage_module, "get_client", lambda: _FakeClient(bucket))

    storage_module.delete_source_file("user-1/notebook-1/source-1/dokument.pdf")

    assert bucket.removed_paths == [["user-1/notebook-1/source-1/dokument.pdf"]]
