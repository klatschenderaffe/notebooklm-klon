from typing import Any

import pytest
from google.genai import types

import app.services.gemini_client as gemini_client


class _FakeEmbedding:
    def __init__(self, values: list[float]) -> None:
        self.values = values


class _FakeEmbedContentResponse:
    def __init__(self, embeddings: list[_FakeEmbedding]) -> None:
        self.embeddings = embeddings


class _FakeModels:
    def __init__(self) -> None:
        self.last_contents: Any = None

    def embed_content(self, model: str, contents: Any, config: Any) -> _FakeEmbedContentResponse:
        self.last_contents = contents
        # Ein FakeEmbedding pro übergebenem Content simulieren, wie die echte API es tut.
        return _FakeEmbedContentResponse([_FakeEmbedding([0.1, 0.2]) for _ in contents])


class _FakeClient:
    def __init__(self) -> None:
        self.models = _FakeModels()


def test_embed_texts_wraps_each_text_as_its_own_content(monkeypatch: pytest.MonkeyPatch) -> None:
    """Regression test: passing contents=[str, str, ...] as a flat list makes the
    Gemini API treat it as ONE multi-part document and return a single embedding no
    matter how many texts were sent in — found live with a 68-chunk Wikipedia article
    (68 texts in, 1 embedding out), silently masked before that by every prior test
    source having exactly one chunk. Each text must be wrapped in its own
    types.Content so the API batches them as N independent documents.
    """
    fake_client = _FakeClient()
    monkeypatch.setattr(gemini_client, "get_client", lambda: fake_client)

    texts = [f"Chunk {i}" for i in range(5)]
    embeddings = gemini_client.embed_texts(texts, task_type="RETRIEVAL_DOCUMENT")

    assert len(embeddings) == len(texts)
    sent_contents = fake_client.models.last_contents
    assert len(sent_contents) == len(texts)
    assert all(isinstance(c, types.Content) for c in sent_contents)
    assert [c.parts[0].text for c in sent_contents] == texts


def test_embed_texts_returns_empty_list_for_no_texts(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_client = _FakeClient()
    monkeypatch.setattr(gemini_client, "get_client", lambda: fake_client)

    assert gemini_client.embed_texts([], task_type="RETRIEVAL_DOCUMENT") == []
    assert fake_client.models.last_contents is None
