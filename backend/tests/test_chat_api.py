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


def test_chat_filters_out_low_similarity_matches(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Regression test: match_chunks returns up to match_count results regardless of
    actual relevance. Found live when a question about dolphins still cited an
    unrelated volcano source (similarity ~0.53) purely because the notebook had too
    few chunks for the RPC to filter it out on its own. The chat endpoint must apply
    its own minimum-similarity cutoff on top of whatever the RPC returns.
    """
    _stub_history(monkeypatch)
    monkeypatch.setattr(chat_router, "embed_texts", lambda texts, task_type: [[0.1, 0.2]])
    monkeypatch.setattr(
        chat_router.vector_store,
        "similarity_search",
        lambda notebook_id, query_embedding, match_count=6: [
            {
                "filename": "delfine.pdf",
                "content": "Relevanter Inhalt über Delfine",
                "similarity": 0.81,
                "id": "1",
                "source_id": "1",
            },
            {
                "filename": "vulkane.md",
                "content": "Irrelevanter Inhalt über Vulkane",
                "similarity": 0.53,
                "id": "2",
                "source_id": "2",
            },
        ],
    )

    received_context: list[str] = []

    def fake_generate_answer(question: str, context_chunks: list[str]) -> str:
        received_context.extend(context_chunks)
        return "Antwort"

    monkeypatch.setattr(chat_router, "generate_answer", fake_generate_answer)

    response = client.post(
        f"/notebooks/{TEST_NOTEBOOK_ID}/chat", json={"question": "Frage zu Delfinen"}
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["citations"]) == 1
    assert body["citations"][0]["filename"] == "delfine.pdf"
    assert received_context == ["Relevanter Inhalt über Delfine"]


def test_chat_still_uses_best_match_when_below_threshold(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Regression test: live gefunden -- eine Markdown-Quelle enthielt die Antwort
    nachweislich, aber der einzige zurückgegebene Treffer lag mit similarity=0.62 knapp
    unter dem Schwellenwert (0.7) und wurde deshalb komplett verworfen, sodass die KI
    ohne jeden Kontext antworten musste ("nicht in den Quellen enthalten"). Der beste
    verfügbare Treffer muss immer verwendet werden, auch wenn er den Schwellenwert
    nicht erreicht."""
    _stub_history(monkeypatch)
    monkeypatch.setattr(chat_router, "embed_texts", lambda texts, task_type: [[0.1, 0.2]])
    monkeypatch.setattr(
        chat_router.vector_store,
        "similarity_search",
        lambda notebook_id, query_embedding, match_count=6: [
            {
                "filename": "everlast-ai.md",
                "content": "Die Stelle betreut die Infrastruktur ...",
                "similarity": 0.62,
                "id": "1",
                "source_id": "1",
            }
        ],
    )

    received_context: list[str] = []

    def fake_generate_answer(question: str, context_chunks: list[str]) -> str:
        received_context.extend(context_chunks)
        return "Antwort"

    monkeypatch.setattr(chat_router, "generate_answer", fake_generate_answer)

    response = client.post(
        f"/notebooks/{TEST_NOTEBOOK_ID}/chat",
        json={"question": "welche Stelle ist aktuell ausgeschrieben?"},
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["citations"]) == 1
    assert body["citations"][0]["filename"] == "everlast-ai.md"
    assert received_context == ["Die Stelle betreut die Infrastruktur ..."]


def test_chat_returns_no_context_when_no_matches_exist(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Die Best-Match-Absicherung darf nicht greifen, wenn das Notebook gar keine
    Quellen/Chunks hat -- dann bleibt der Kontext leer, statt mit einem `IndexError`
    auf all_matches[0] abzustürzen."""
    _stub_history(monkeypatch)
    monkeypatch.setattr(chat_router, "embed_texts", lambda texts, task_type: [[0.1, 0.2]])
    monkeypatch.setattr(
        chat_router.vector_store,
        "similarity_search",
        lambda notebook_id, query_embedding, match_count=6: [],
    )

    received_context: list[str] = []

    def fake_generate_answer(question: str, context_chunks: list[str]) -> str:
        received_context.extend(context_chunks)
        return "Antwort"

    monkeypatch.setattr(chat_router, "generate_answer", fake_generate_answer)

    response = client.post(
        f"/notebooks/{TEST_NOTEBOOK_ID}/chat", json={"question": "Irgendeine Frage"}
    )

    assert response.status_code == 200
    assert response.json()["citations"] == []
    assert received_context == []


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
