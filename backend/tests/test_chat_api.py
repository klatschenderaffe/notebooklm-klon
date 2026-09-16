import pytest
from fastapi.testclient import TestClient

import app.routers.chat as chat_router
from app.main import app

client = TestClient(app)


def test_chat_returns_answer_with_citations(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(chat_router, "embed_texts", lambda texts, task_type: [[0.1, 0.2]])
    monkeypatch.setattr(
        chat_router.vector_store,
        "similarity_search",
        lambda query_embedding, match_count=6: [
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

    response = client.post("/chat", json={"question": "Was steht in der Datei?"})

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "Die Antwort."
    assert body["citations"][0]["filename"] == "notiz.md"
