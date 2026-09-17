from typing import Any

import pytest

import app.services.history_store as history_store


class _FakeQuery:
    def __init__(self, table: "_FakeTable", op: str) -> None:
        self.table = table
        self.op = op
        self.filters: dict[str, Any] = {}
        self.payload: Any = None

    def insert(self, payload: Any) -> "_FakeQuery":
        self.payload = payload
        return self

    def select(self, *_args: Any) -> "_FakeQuery":
        return self

    def eq(self, field: str, value: Any) -> "_FakeQuery":
        self.filters[field] = value
        return self

    def order(self, *_args: Any, **_kwargs: Any) -> "_FakeQuery":
        return self

    def execute(self) -> Any:
        self.table.calls.append((self.op, self.filters, self.payload))
        return self.table.response


class _FakeTable:
    def __init__(self, response_data: list[dict[str, Any]]) -> None:
        self.calls: list[tuple] = []
        self.response = type("Response", (), {"data": response_data})()

    def insert(self, payload: Any) -> _FakeQuery:
        return _FakeQuery(self, "insert").insert(payload)

    def select(self, *args: Any) -> _FakeQuery:
        return _FakeQuery(self, "select").select(*args)


class _FakeClient:
    def __init__(self, table: _FakeTable) -> None:
        self._table = table

    def table(self, name: str) -> _FakeTable:
        return self._table


def test_insert_chat_message(monkeypatch: pytest.MonkeyPatch) -> None:
    table = _FakeTable([{"id": "1", "role": "user", "content": "Frage", "citations": []}])
    monkeypatch.setattr(history_store, "get_client", lambda: _FakeClient(table))

    result = history_store.insert_chat_message("nb-1", "user", "Frage", [])

    assert result["content"] == "Frage"
    op, _filters, payload = table.calls[0]
    assert op == "insert"
    assert payload["notebook_id"] == "nb-1"
    assert payload["role"] == "user"


def test_insert_presentation(monkeypatch: pytest.MonkeyPatch) -> None:
    table = _FakeTable([{"id": "1", "title": "Titel"}])
    monkeypatch.setattr(history_store, "get_client", lambda: _FakeClient(table))

    result = history_store.insert_presentation(
        "nb-1", "Titel", "Thema", "path/to/file.pptx", {"accent_color": "#16A34A"}
    )

    assert result["title"] == "Titel"
    _op, _filters, payload = table.calls[0]
    assert payload["storage_path"] == "path/to/file.pptx"


def test_get_presentation_returns_none_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    table = _FakeTable([])
    monkeypatch.setattr(history_store, "get_client", lambda: _FakeClient(table))

    result = history_store.get_presentation("nb-1", "missing-id")

    assert result is None
