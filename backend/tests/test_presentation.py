import io

from pptx import Presentation

from app.services.design import DEFAULT_DESIGN
from app.services.presentation import build_presentation


def _all_text(slide) -> str:  # type: ignore[no-untyped-def]
    parts = []
    for shape in slide.shapes:
        if shape.has_text_frame:
            parts.append(shape.text_frame.text)
    return "\n".join(parts)


def test_build_presentation_creates_title_and_content_slides() -> None:
    slides = [
        {"title": "Einleitung", "bullets": ["Punkt A", "Punkt B"]},
        {"title": "Fazit", "bullets": ["Zusammenfassung"]},
    ]

    pptx_bytes = build_presentation("Meine Präsentation", slides)
    prs = Presentation(io.BytesIO(pptx_bytes))

    assert len(prs.slides) == 3
    assert "Meine Präsentation" in _all_text(prs.slides[0])
    assert "Einleitung" in _all_text(prs.slides[1])
    assert "Punkt A" in _all_text(prs.slides[1])
    assert "Fazit" in _all_text(prs.slides[2])


def test_build_presentation_uses_widescreen_format() -> None:
    pptx_bytes = build_presentation("Titel", [{"title": "Folie", "bullets": ["X"]}])
    prs = Presentation(io.BytesIO(pptx_bytes))

    assert prs.slide_width is not None and prs.slide_height is not None
    assert round(prs.slide_width / prs.slide_height, 2) == round(16 / 9, 2)


def test_build_presentation_without_slides_adds_placeholder() -> None:
    pptx_bytes = build_presentation("Leer", [])
    prs = Presentation(io.BytesIO(pptx_bytes))

    assert len(prs.slides) == 2


def test_build_presentation_applies_custom_design_colors() -> None:
    design = {
        "background_color": "#112233",
        "accent_color": "#AABBCC",
        "text_color": "#FFFFFF",
        "heading_font": "Georgia",
        "body_font": "Arial",
    }
    pptx_bytes = build_presentation(
        "Titel", [{"title": "Folie", "bullets": ["X"]}], design=design
    )
    prs = Presentation(io.BytesIO(pptx_bytes))

    bg = prs.slides[0].background.fill.fore_color.rgb
    assert str(bg) == "112233"


def test_build_presentation_falls_back_to_default_design_when_none_given() -> None:
    pptx_bytes = build_presentation("Titel", [{"title": "Folie", "bullets": ["X"]}])
    prs = Presentation(io.BytesIO(pptx_bytes))

    bg = prs.slides[0].background.fill.fore_color.rgb
    assert str(bg) == DEFAULT_DESIGN["background_color"].lstrip("#")
