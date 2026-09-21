from typing import Any

import pytest
from fastapi import HTTPException
from google.genai import errors as genai_errors
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


class _FakeGenerateContentResponse:
    def __init__(self, text: str) -> None:
        self.text = text


class _FailingModels:
    """Simuliert einen fehlschlagenden Gemini-API-Call (Kontingent erschöpft, Service
    down, etc.), wie live bereits mit transienten 503 "high demand"-Fehlern
    beobachtet."""

    def generate_content(self, model: str, contents: Any, config: Any) -> Any:
        raise genai_errors.APIError(503, {"message": "The model is overloaded."})


class _FailingClient:
    def __init__(self) -> None:
        self.models = _FailingModels()


class _RespondingModels:
    def __init__(self, text: str) -> None:
        self._text = text

    def generate_content(self, model: str, contents: Any, config: Any) -> Any:
        return _FakeGenerateContentResponse(self._text)


class _RespondingClient:
    def __init__(self, text: str) -> None:
        self.models = _RespondingModels(text)


def test_generate_answer_raises_503_on_api_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Regression test: ein fehlschlagender Gemini-Call darf nicht ungefangen bis zum
    generischen 500-Handler durchschlagen, sondern muss als klare 503 erkennbar sein."""
    monkeypatch.setattr(gemini_client, "get_client", lambda: _FailingClient())

    with pytest.raises(HTTPException) as exc_info:
        gemini_client.generate_answer("Frage", ["Kontext"])

    assert exc_info.value.status_code == 503


def test_generate_presentation_outline_raises_503_on_api_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(gemini_client, "get_client", lambda: _FailingClient())

    with pytest.raises(HTTPException) as exc_info:
        gemini_client.generate_presentation_outline("Thema", ["Kontext"])

    assert exc_info.value.status_code == 503


def test_generate_presentation_outline_raises_422_on_invalid_json(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Regression test: liefert Gemini trotz response_mime_type='application/json'
    ausnahmsweise kein valides JSON, darf keine rohe JSONDecodeError durchschlagen."""
    monkeypatch.setattr(gemini_client, "get_client", lambda: _RespondingClient("nicht-json{{"))

    with pytest.raises(HTTPException) as exc_info:
        gemini_client.generate_presentation_outline("Thema", ["Kontext"])

    assert exc_info.value.status_code == 422
