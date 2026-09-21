import json
import logging
import time
from collections.abc import Callable
from functools import lru_cache
from typing import Any, cast

import httpx
from fastapi import HTTPException
from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from app.config import settings
from app.services.design import ALLOWED_FONTS

logger = logging.getLogger(__name__)

GEMINI_UNAVAILABLE_DETAIL = (
    "KI-Service ist momentan nicht verfügbar. Bitte versuche es später erneut."
)

# Live beobachtet (21.09.): ohne explizites Timeout wartet die SDK laut eigenem Quellcode
# (_api_client.py, max_allowed_time = float('inf') falls http_options.timeout None ist)
# potenziell unbegrenzt lange auf eine Antwort. Bei Googles "high demand"-Zustand kam die
# 503-Antwort dadurch teils erst nach über zwei Minuten -- gefühlt ein Hänger, technisch
# kein Fehler, aber für den Nutzer ununterscheidbar von einem echten Absturz. 30s deckt
# normale, auch etwas langsamere Antworten (z.B. längere Präsentationsgliederungen) ab,
# begrenzt aber den Extremfall auf ein erträgliches Maß -- vor allem in Kombination mit
# Retry + Fallback unten, die sonst im schlimmsten Fall Minuten aufaddieren würden.
_REQUEST_TIMEOUT_MS = 30_000


def _call_with_retry[T](fn: Callable[[], T], *, retry_delay_seconds: float = 1.5) -> T:
    """Ruft `fn` auf und versucht es genau einmal erneut, falls Gemini mit einem
    `ServerError` (5xx) antwortet oder die Anfrage das Timeout überschreitet (siehe
    _REQUEST_TIMEOUT_MS) -- live wiederholt beobachtete "high demand"-503er sind laut
    Googles eigener Fehlermeldung ausdrücklich "usually temporary", ein Timeout unter
    Last ist strukturell gleich zu behandeln. Ein einziger Retry mit kurzer Pause fängt
    genau diesen häufigsten Fall ab, ohne bei einem echten, andauernden Ausfall spürbar
    Zeit zu verschwenden. `ClientError` (4xx, z.B. ungültiger API-Key oder Kontingent
    dauerhaft aufgebraucht) wird bewusst NICHT wiederholt -- ein erneuter Versuch würde
    dort nichts ändern."""
    try:
        return fn()
    except (genai_errors.ServerError, httpx.TimeoutException) as exc:
        logger.warning(
            "Gemini-ServerError/Timeout, wiederhole einmal nach %.1fs: %s",
            retry_delay_seconds,
            exc,
        )
        time.sleep(retry_delay_seconds)
        return fn()


_QUOTA_EXCEEDED_STATUS_CODE = 429


def _generate_content_with_fallback(contents: Any, config: types.GenerateContentConfig) -> Any:
    """Ruft generate_content mit dem primären Chat-Modell auf und weicht auf ein
    zweites, unabhängiges Modell aus, statt denselben Modell-Endpunkt erneut zu
    versuchen, wenn entweder:

    - ein ServerError/Timeout auftritt (live beobachtet: sowohl gemini-3.6-flash als
      auch später am selben Tag gemini-3.7-flash gerieten unabhängig voneinander in
      Googles "high demand"-Zustand), oder
    - ein ClientError mit Status 429 (Kontingent erschöpft) auftritt. Live gefunden:
      die Fehlermeldung selbst zeigt, dass das Kontingent PRO MODELL gilt
      ("quotaId": "GenerateRequestsPerDayPerProjectPerModel-FreeTier",
      "quotaDimensions": {"model": "gemini-3.7-flash"}) -- ein Fallback auf ein
      anderes Modell mit eigenem, unabhängigem Kontingent-Topf kann hier tatsächlich
      helfen.

    Bewusst KEIN Retry auf demselben Modell mehr (anders als in einer früheren
    Version): live am 21.09. wiederholt beobachtet, dass ein Retry auf demselben
    Modell während einer anhaltenden Störung praktisch nie half, aber bei einem
    Timeout von 30s pro Versuch (_REQUEST_TIMEOUT_MS) die Gesamt-Wartezeit auf bis zu
    4 Versuche (2x primär + 2x Fallback, ca. 120s im schlimmsten Fall) aufsummierte --
    für den Nutzer als "hängt ewig" wahrgenommen. Jetzt nur noch primär → Fallback
    (max. 2 Versuche, ca. 60s im schlimmsten Fall). Bei einer kurzen, echten Spitze
    übernimmt das Fallback-Modell die Rolle des früheren Retries; bei einer
    andauernden Störung wird der Fehler dafür doppelt so schnell klar erkennbar."""
    try:
        return get_client().models.generate_content(
            model=settings.gemini_chat_model, contents=contents, config=config
        )
    except (genai_errors.ServerError, httpx.TimeoutException) as exc:
        logger.warning(
            "Primäres Chat-Modell %s überlastet, weiche auf Fallback-Modell %s aus: %s",
            settings.gemini_chat_model,
            settings.gemini_chat_model_fallback,
            exc,
        )
    except genai_errors.ClientError as exc:
        if exc.code != _QUOTA_EXCEEDED_STATUS_CODE:
            raise
        logger.warning(
            "Primäres Chat-Modell %s hat Kontingent erschöpft, weiche auf %s aus: %s",
            settings.gemini_chat_model,
            settings.gemini_chat_model_fallback,
            exc,
        )
    return get_client().models.generate_content(
        model=settings.gemini_chat_model_fallback, contents=contents, config=config
    )


SYSTEM_INSTRUCTION = (
    "Du bist ein Assistent, der ausschließlich auf Basis der bereitgestellten Quellenausschnitte "
    "antwortet. Nutze kein externes Wissen. Wenn die Antwort nicht in den Quellen enthalten ist, "
    "sag das explizit, anstatt zu spekulieren. Antworte auf Deutsch."
)

OUTLINE_INSTRUCTION = (
    "Du erstellst eine prägnante Präsentationsgliederung ausschließlich auf Basis der "
    "bereitgestellten Quellenausschnitte. Nutze kein externes Wissen. Antworte auf Deutsch."
)


@lru_cache
def get_client() -> genai.Client:
    return genai.Client(
        api_key=settings.gemini_api_key,
        http_options=types.HttpOptions(timeout=_REQUEST_TIMEOUT_MS),
    )


def embed_texts(texts: list[str], task_type: str) -> list[list[float]]:
    if not texts:
        return []
    # WICHTIG: contents=[str, str, ...] als flache Liste wird von der API als EIN
    # Multi-Part-Dokument interpretiert und liefert dadurch nur ein einziges Embedding
    # zurück, unabhängig von der Anzahl der Texte — live verifiziert (68 Strings rein,
    # 1 Embedding raus). Bei genau einem Chunk pro Quelle (der bisherige Testfall) fiel
    # das nicht auf, da "1 raus" dort zufällig korrekt aussah. Jeder Text muss stattdessen
    # als eigenständiges types.Content-Objekt übergeben werden, damit die API sie als N
    # unabhängige Dokumente batcht und N Embeddings zurückgibt (live mit 68 Chunks
    # verifiziert: 68 rein, 68 raus).
    contents = [types.Content(parts=[types.Part(text=t)]) for t in texts]
    # Bisher fehlte hier (anders als bei generate_answer/generate_presentation_outline)
    # der APIError-Fang -- ein anhaltender Gemini-Fehler beim Embedding schlug dadurch
    # ungefangen bis zum generischen 500-Handler durch, statt als klare 503 erkennbar
    # zu sein. Live in Sentry mehrfach als "Unhandled" auf genau diesem Pfad markiert.
    try:
        response = _call_with_retry(
            lambda: get_client().models.embed_content(
                model=settings.gemini_embedding_model,
                contents=cast(Any, contents),
                config=types.EmbedContentConfig(
                    output_dimensionality=settings.gemini_embedding_dimensions,
                    task_type=task_type,
                ),
            )
        )
    except (genai_errors.APIError, httpx.TimeoutException) as exc:
        logger.warning("Gemini-API-Fehler bei embed_texts: %s", exc)
        raise HTTPException(status_code=503, detail=GEMINI_UNAVAILABLE_DETAIL) from exc
    return [list(embedding.values or []) for embedding in response.embeddings or []]


def generate_answer(question: str, context_chunks: list[str]) -> str:
    context = "\n\n---\n\n".join(context_chunks) if context_chunks else "(keine Quellen gefunden)"
    prompt = f"Quellenausschnitte:\n\n{context}\n\nFrage: {question}"
    # Kontingent erschöpft oder Service down (live beobachtet: transiente 503 "high
    # demand"-Fehler, siehe PROGRESS.md) propagieren sonst ungefangen bis zum
    # generischen 500-Handler, statt dem Nutzer verständlich zu machen, dass es an der
    # KI liegt und ein erneuter Versuch sinnvoll ist. _call_with_retry versucht einen
    # 5xx-Fehler zuerst automatisch einmal erneut (siehe dort), bevor überhaupt eine
    # Fehlermeldung beim Nutzer ankommt.
    try:
        response = _generate_content_with_fallback(
            contents=prompt,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION),
        )
    except (genai_errors.APIError, httpx.TimeoutException) as exc:
        logger.warning("Gemini-API-Fehler bei generate_answer: %s", exc)
        raise HTTPException(status_code=503, detail=GEMINI_UNAVAILABLE_DETAIL) from exc
    return response.text or ""


def generate_presentation_outline(
    topic: str,
    context_chunks: list[str],
    design_description: str | None = None,
    tone: str | None = None,
    slide_count_hint: str | None = None,
) -> dict[str, Any]:
    context = "\n\n---\n\n".join(context_chunks)
    instructions = [f"Erstelle eine Präsentationsgliederung zum Thema: {topic}"]
    if tone:
        instructions.append(f"Sprachlicher Stil/Ton der Texte: {tone}")
    if slide_count_hint:
        instructions.append(f"Ungefähre gewünschte Foliezahl (ohne Titelfolie): {slide_count_hint}")
    if design_description:
        instructions.append(f"Gewünschtes visuelles Design (Farben/Stimmung): {design_description}")
    else:
        instructions.append(
            "Kein Design gewünscht — wähle ein neutrales, modernes, gut lesbares Farbschema."
        )
    instructions.append(f"Quellenausschnitte:\n\n{context}")
    prompt = "\n\n".join(instructions)

    font_enum = ALLOWED_FONTS
    response_schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "design": {
                "type": "object",
                "description": (
                    "Farbschema passend zur gewünschten Design-Beschreibung "
                    "(oder neutral/modern falls keine angegeben ist). "
                    "background_color/accent_color/text_color müssen Hex-Farbcodes "
                    "im Format #RRGGBB sein, mit gutem Kontrast zwischen text_color "
                    "und background_color."
                ),
                "properties": {
                    "background_color": {"type": "string"},
                    "accent_color": {"type": "string"},
                    "text_color": {"type": "string"},
                    "heading_font": {"type": "string", "enum": font_enum},
                    "body_font": {"type": "string", "enum": font_enum},
                },
                "required": [
                    "background_color",
                    "accent_color",
                    "text_color",
                    "heading_font",
                    "body_font",
                ],
            },
            "slides": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "bullets": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["title", "bullets"],
                },
            },
        },
        "required": ["title", "design", "slides"],
    }

    # Gleiche Absicherung wie generate_answer() -- beide rufen dieselbe Art API auf und
    # sollen bei Kontingent-/Service-Fehlern konsistent mit 503 statt einem generischen
    # 500 antworten, inklusive des automatischen Einmal-Retries bei 5xx.
    try:
        response = _generate_content_with_fallback(
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=OUTLINE_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=response_schema,
            ),
        )
    except (genai_errors.APIError, httpx.TimeoutException) as exc:
        logger.warning("Gemini-API-Fehler bei generate_presentation_outline: %s", exc)
        raise HTTPException(status_code=503, detail=GEMINI_UNAVAILABLE_DETAIL) from exc

    # Trotz response_mime_type="application/json" liefert Gemini ausnahmsweise kein
    # valides JSON zurück -- ein rohes json.loads() würde hier mit JSONDecodeError bis
    # zum generischen 500-Handler durchschlagen, statt dem Nutzer klarzumachen, dass
    # die KI-Antwort diesmal nicht verwertbar war.
    try:
        return cast(dict[str, Any], json.loads(response.text or "{}"))
    except json.JSONDecodeError as exc:
        logger.warning("Ungültiges JSON von Gemini bei generate_presentation_outline: %s", exc)
        raise HTTPException(
            status_code=422,
            detail=(
                "Präsentationsgliederung konnte nicht verarbeitet werden "
                "(ungültiges Format von der KI)"
            ),
        ) from exc
