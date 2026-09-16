import json
from functools import lru_cache
from typing import Any, cast

from google import genai
from google.genai import types

from app.config import settings
from app.services.design import ALLOWED_FONTS

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
        instructions.append(
            f"Gewünschtes visuelles Design (Farben/Stimmung): {design_description}"
        )
    else:
        instructions.append(
            "Kein Design gewünscht — wähle ein neutrales, modernes, gut lesbares Farbschema."
        )
    instructions.append(f"Quellenausschnitte:\n\n{context}")
    prompt = "\n\n".join(instructions)

    font_enum = ALLOWED_FONTS
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
            },
        ),
    )
    return cast(dict[str, Any], json.loads(response.text or "{}"))
