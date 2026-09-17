from typing import Any

import pytest

import app.services.notes_store as notes_store


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

    def delete(self) -> "_FakeQuery":
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

    def delete(self) -> _FakeQuery:
        return _FakeQuery(self, "delete").delete()


class _FakeClient:
    def __init__(self, table: _FakeTable) -> None:
        self._table = table

    def table(self, name: str) -> _FakeTable:
        return self._table


def test_insert_note(monkeypatch: pytest.MonkeyPatch) -> None:
    table = _FakeTable([{"id": "n1", "content": "Wichtiger Punkt", "created_at": "2026-09-17"}])
    monkeypatch.setattr(notes_store, "get_client", lambda: _FakeClient(table))

    result = notes_store.insert_note("source-1", "Wichtiger Punkt")

    assert result["content"] == "Wichtiger Punkt"
    op, _filters, payload = table.calls[0]
    assert op == "insert"
    assert payload["source_id"] == "source-1"
    assert payload["content"] == "Wichtiger Punkt"


def test_list_notes_filters_by_source(monkeypatch: pytest.MonkeyPatch) -> None:
    table = _FakeTable([{"id": "n1", "content": "Notiz 1"}])
    monkeypatch.setattr(notes_store, "get_client", lambda: _FakeClient(table))

    result = notes_store.list_notes("source-1")

    assert result == [{"id": "n1", "content": "Notiz 1"}]
    _op, filters, _payload = table.calls[0]
    assert filters == {"source_id": "source-1"}


def test_delete_note_returns_true_when_deleted(monkeypatch: pytest.MonkeyPatch) -> None:
    table = _FakeTable([{"id": "n1"}])
    monkeypatch.setattr(notes_store, "get_client", lambda: _FakeClient(table))

    assert notes_store.delete_note("source-1", "n1") is True
    _op, filters, _payload = table.calls[0]
    assert filters == {"id": "n1", "source_id": "source-1"}


def test_delete_note_returns_false_when_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    table = _FakeTable([])
    monkeypatch.setattr(notes_store, "get_client", lambda: _FakeClient(table))

    assert notes_store.delete_note("source-1", "missing") is False
