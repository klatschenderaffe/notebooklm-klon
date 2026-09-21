from typing import Any

import httpx
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


class _FailingEmbedModels:
    def embed_content(self, model: str, contents: Any, config: Any) -> Any:
        raise genai_errors.APIError(503, {"message": "embedding service down"})


class _FailingEmbedClient:
    def __init__(self) -> None:
        self.models = _FailingEmbedModels()


def test_embed_texts_raises_503_on_api_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Regression test: embed_texts() hatte bisher (anders als generate_answer/
    generate_presentation_outline) keinen APIError-Fang -- ein anhaltender
    Gemini-Fehler beim Embedding schlug dadurch ungefangen bis zum generischen
    500-Handler durch, statt als klare 503 erkennbar zu sein (live in Sentry mehrfach
    als "Unhandled" auf genau diesem Pfad markiert)."""
    monkeypatch.setattr(gemini_client, "get_client", lambda: _FailingEmbedClient())

    with pytest.raises(HTTPException) as exc_info:
        gemini_client.embed_texts(["Text"], task_type="RETRIEVAL_DOCUMENT")

    assert exc_info.value.status_code == 503


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


def test_call_with_retry_retries_once_on_server_error_then_succeeds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """_call_with_retry() wird nicht mehr von _generate_content_with_fallback()
    verwendet (siehe dort -- bewusst kein Gleich-Modell-Retry mehr, um die
    Gesamt-Wartezeit zu begrenzen), aber weiterhin von embed_texts(). Direkter Test
    der Helper-Funktion selbst, um die Retry-Erfolg-Abdeckung zu erhalten."""
    monkeypatch.setattr(gemini_client.time, "sleep", lambda _seconds: None)
    call_count = 0

    def flaky() -> str:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise genai_errors.ServerError(503, {"message": "high demand"})
        return "Ergebnis"

    result = gemini_client._call_with_retry(flaky)

    assert result == "Ergebnis"
    assert call_count == 2


def test_call_with_retry_retries_once_on_timeout_then_succeeds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(gemini_client.time, "sleep", lambda _seconds: None)
    call_count = 0

    def flaky() -> str:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise httpx.ReadTimeout("Zeitüberschreitung")
        return "Ergebnis"

    result = gemini_client._call_with_retry(flaky)

    assert result == "Ergebnis"
    assert call_count == 2


class _AlwaysServerErrorModels:
    def __init__(self) -> None:
        self.call_count = 0

    def generate_content(self, model: str, contents: Any, config: Any) -> Any:
        self.call_count += 1
        raise genai_errors.ServerError(503, {"message": "still overloaded"})


class _AlwaysServerErrorClient:
    def __init__(self) -> None:
        self.models = _AlwaysServerErrorModels()


def test_generate_answer_gives_up_with_503_when_both_models_overloaded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Hält der ServerError beim primären Modell an, wird das Fallback-Modell versucht
    (siehe test_generate_answer_falls_back_to_second_model_when_primary_overloaded);
    hält der ServerError auch dort an, muss es sauber als 503 beim Nutzer ankommen.
    Bewusst KEIN Retry mehr auf demselben Modell (siehe
    _generate_content_with_fallback) -- genau ein Versuch pro Modell, dann Fallback,
    dann Aufgabe, um die Gesamt-Wartezeit zu begrenzen."""
    fake_client = _AlwaysServerErrorClient()
    monkeypatch.setattr(gemini_client, "get_client", lambda: fake_client)

    with pytest.raises(HTTPException) as exc_info:
        gemini_client.generate_answer("Frage", ["Kontext"])

    assert exc_info.value.status_code == 503
    # Ein Versuch primäres Modell + ein Versuch Fallback-Modell, kein Retry mehr.
    assert fake_client.models.call_count == 2


class _PrimaryFailsFallbackSucceedsModels:
    """Simuliert das live am 21.09. beobachtete Muster: das primäre Chat-Modell ist
    überlastet, ein unabhängiges zweites (Fallback-)Modell antwortet aber normal --
    genau der Fall, für den _generate_content_with_fallback eingeführt wurde."""

    def __init__(self, fallback_text: str) -> None:
        self._fallback_text = fallback_text
        self.calls: list[str] = []

    def generate_content(self, model: str, contents: Any, config: Any) -> Any:
        self.calls.append(model)
        if model == gemini_client.settings.gemini_chat_model:
            raise genai_errors.ServerError(503, {"message": "high demand"})
        return _FakeGenerateContentResponse(self._fallback_text)


class _PrimaryFailsFallbackSucceedsClient:
    def __init__(self, fallback_text: str) -> None:
        self.models = _PrimaryFailsFallbackSucceedsModels(fallback_text)


def test_generate_answer_falls_back_to_second_model_when_primary_overloaded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_client = _PrimaryFailsFallbackSucceedsClient("Antwort vom Fallback-Modell")
    monkeypatch.setattr(gemini_client, "get_client", lambda: fake_client)

    answer = gemini_client.generate_answer("Frage", ["Kontext"])

    assert answer == "Antwort vom Fallback-Modell"
    # Kein Retry auf dem primären Modell mehr -- ein Versuch primär, direkt gefolgt
    # vom Fallback-Modell.
    assert fake_client.models.calls == [
        gemini_client.settings.gemini_chat_model,
        gemini_client.settings.gemini_chat_model_fallback,
    ]


class _AlwaysTimingOutModels:
    def __init__(self) -> None:
        self.call_count = 0

    def generate_content(self, model: str, contents: Any, config: Any) -> Any:
        self.call_count += 1
        raise httpx.ReadTimeout("Zeitüberschreitung")


class _AlwaysTimingOutClient:
    def __init__(self) -> None:
        self.models = _AlwaysTimingOutModels()


def test_generate_answer_gives_up_with_503_when_everything_times_out(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Hält das Timeout beim primären UND beim Fallback-Modell an, muss weiterhin
    sauber als 503 beim Nutzer ankommen, statt eines generischen 500 (httpx.TimeoutException
    ist keine google.genai.errors.APIError und würde ohne den erweiterten Fang
    ungefangen durchschlagen)."""
    fake_client = _AlwaysTimingOutClient()
    monkeypatch.setattr(gemini_client, "get_client", lambda: fake_client)

    with pytest.raises(HTTPException) as exc_info:
        gemini_client.generate_answer("Frage", ["Kontext"])

    assert exc_info.value.status_code == 503
    # Ein Versuch primäres Modell + ein Versuch Fallback-Modell, kein Retry mehr.
    assert fake_client.models.call_count == 2


class _PrimaryQuotaExceededFallbackSucceedsModels:
    """Simuliert den live gefundenen Fall: das Tages-/Modell-Kontingent des primären
    Chat-Modells ist erschöpft (429 RESOURCE_EXHAUSTED, quotaDimensions.model zeigt
    explizit das primäre Modell) -- das unabhängige Fallback-Modell hat ein eigenes,
    noch nicht erschöpftes Kontingent und antwortet normal."""

    def __init__(self, fallback_text: str) -> None:
        self._fallback_text = fallback_text
        self.calls: list[str] = []

    def generate_content(self, model: str, contents: Any, config: Any) -> Any:
        self.calls.append(model)
        if model == gemini_client.settings.gemini_chat_model:
            raise genai_errors.ClientError(429, {"message": "quota exceeded"})
        return _FakeGenerateContentResponse(self._fallback_text)


class _PrimaryQuotaExceededFallbackSucceedsClient:
    def __init__(self, fallback_text: str) -> None:
        self.models = _PrimaryQuotaExceededFallbackSucceedsModels(fallback_text)


def test_generate_answer_falls_back_when_primary_quota_exceeded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_client = _PrimaryQuotaExceededFallbackSucceedsClient("Antwort vom Fallback-Modell")
    monkeypatch.setattr(gemini_client, "get_client", lambda: fake_client)

    answer = gemini_client.generate_answer("Frage", ["Kontext"])

    assert answer == "Antwort vom Fallback-Modell"
    # Kein Retry auf dem primären Modell (429 wird bewusst nicht wiederholt) -- nur ein
    # Aufruf des primären Modells, direkt gefolgt vom Fallback-Modell.
    assert fake_client.models.calls == [
        gemini_client.settings.gemini_chat_model,
        gemini_client.settings.gemini_chat_model_fallback,
    ]


def test_generate_answer_gives_up_with_503_when_both_models_quota_exceeded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _AlwaysQuotaExceededModels:
        def __init__(self) -> None:
            self.call_count = 0

        def generate_content(self, model: str, contents: Any, config: Any) -> Any:
            self.call_count += 1
            raise genai_errors.ClientError(429, {"message": "quota exceeded"})

    class _AlwaysQuotaExceededClient:
        def __init__(self) -> None:
            self.models = _AlwaysQuotaExceededModels()

    fake_client = _AlwaysQuotaExceededClient()
    monkeypatch.setattr(gemini_client, "get_client", lambda: fake_client)

    with pytest.raises(HTTPException) as exc_info:
        gemini_client.generate_answer("Frage", ["Kontext"])

    assert exc_info.value.status_code == 503
    assert fake_client.models.call_count == 2


def test_generate_answer_does_not_fall_back_on_non_quota_client_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ein ClientError, der KEIN Kontingent-Fehler ist (z.B. 400 durch eine ungültige
    Anfrage), würde durch einen Modellwechsel nicht behoben -- muss also weiterhin
    direkt als 503 durchschlagen, ohne das Fallback-Modell unnötig zu belasten."""

    class _InvalidRequestModels:
        def __init__(self) -> None:
            self.call_count = 0

        def generate_content(self, model: str, contents: Any, config: Any) -> Any:
            self.call_count += 1
            raise genai_errors.ClientError(400, {"message": "invalid request"})

    class _InvalidRequestClient:
        def __init__(self) -> None:
            self.models = _InvalidRequestModels()

    fake_client = _InvalidRequestClient()
    monkeypatch.setattr(gemini_client, "get_client", lambda: fake_client)

    with pytest.raises(HTTPException) as exc_info:
        gemini_client.generate_answer("Frage", ["Kontext"])

    assert exc_info.value.status_code == 503
    assert fake_client.models.call_count == 1


def test_embed_texts_raises_503_on_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    class _TimingOutEmbedModels:
        def embed_content(self, model: str, contents: Any, config: Any) -> Any:
            raise httpx.ReadTimeout("Zeitüberschreitung")

    class _TimingOutEmbedClient:
        def __init__(self) -> None:
            self.models = _TimingOutEmbedModels()

    monkeypatch.setattr(gemini_client.time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(gemini_client, "get_client", lambda: _TimingOutEmbedClient())

    with pytest.raises(HTTPException) as exc_info:
        gemini_client.embed_texts(["Text"], task_type="RETRIEVAL_DOCUMENT")

    assert exc_info.value.status_code == 503
