import pytest
from fastapi.testclient import TestClient

import app.routers.chat as chat_router
from tests.conftest import TEST_NOTEBOOK_ID


def _stub_history(monkeypatch: pytest.MonkeyPatch) -> list[tuple]:
    calls: list[tuple] = []
    monkeypatch.setattr(
        chat_router.history_store,
        "insert_chat_message",
        lambda notebook_id, role, content, citations: calls.append(
            (notebook_id, role, content, citations)
        ),
    )
    return calls


def test_chat_returns_answer_with_citations(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    history_calls = _stub_history(monkeypatch)
    monkeypatch.setattr(chat_router, "embed_texts", lambda texts, task_type: [[0.1, 0.2]])
    monkeypatch.setattr(
        chat_router.vector_store,
        "similarity_search",
        lambda notebook_id, query_embedding, match_count=6: [
            {
                "filename": "notiz.md",
                "content": "Relevanter Inhalt",
                "similarity": 0.9,
                "id": "1",
                "source_id": "1",
            }
        ],
    )
    monkeypatch.setattr(
        chat_router, "generate_answer", lambda question, context_chunks: "Die Antwort."
    )

    response = client.post(
        f"/notebooks/{TEST_NOTEBOOK_ID}/chat", json={"question": "Was steht in der Datei?"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "Die Antwort."
    assert body["citations"][0]["filename"] == "notiz.md"
    assert history_calls[0][1] == "user"
    assert history_calls[1][1] == "assistant"
    assert history_calls[1][2] == "Die Antwort."


def test_get_chat_history(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        chat_router.history_store,
        "list_chat_messages",
        lambda notebook_id: [
            {
                "id": "1",
                "role": "user",
                "content": "Frage",
                "citations": [],
                "created_at": "2026-09-17T00:00:00Z",
            }
        ],
    )
    response = client.get(f"/notebooks/{TEST_NOTEBOOK_ID}/chat/history")
    assert response.status_code == 200
    assert response.json()[0]["content"] == "Frage"
