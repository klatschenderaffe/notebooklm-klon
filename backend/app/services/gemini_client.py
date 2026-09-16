import json
from functools import lru_cache
from typing import Any, cast

from google import genai
from google.genai import types

from app.config import settings

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
    return genai.Client(api_key=settings.gemini_api_key)


def embed_texts(texts: list[str], task_type: str) -> list[list[float]]:
    if not texts:
        return []
    response = get_client().models.embed_content(
        model=settings.gemini_embedding_model,
        contents=cast(Any, texts),
        config=types.EmbedContentConfig(
            output_dimensionality=settings.gemini_embedding_dimensions,
            task_type=task_type,
        ),
    )
    return [list(embedding.values or []) for embedding in response.embeddings or []]


def generate_answer(question: str, context_chunks: list[str]) -> str:
    context = "\n\n---\n\n".join(context_chunks) if context_chunks else "(keine Quellen gefunden)"
    prompt = f"Quellenausschnitte:\n\n{context}\n\nFrage: {question}"
    response = get_client().models.generate_content(
        model=settings.gemini_chat_model,
        contents=prompt,
        config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION),
    )
    return response.text or ""


def generate_presentation_outline(topic: str, context_chunks: list[str]) -> dict[str, Any]:
    context = "\n\n---\n\n".join(context_chunks)
    prompt = (
        f"Erstelle eine Präsentationsgliederung zum Thema: {topic}\n\n"
        f"Quellenausschnitte:\n\n{context}"
    )
    response = get_client().models.generate_content(
        model=settings.gemini_chat_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=OUTLINE_INSTRUCTION,
            response_mime_type="application/json",
            response_schema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
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
                "required": ["title", "slides"],
            },
        ),
    )
    return cast(dict[str, Any], json.loads(response.text or "{}"))
