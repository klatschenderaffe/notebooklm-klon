import io
from typing import Any

from pptx import Presentation
from pptx.util import Inches, Pt


def build_presentation(title: str, slides: list[dict[str, Any]]) -> bytes:
    prs = Presentation()

    title_slide = prs.slides.add_slide(prs.slide_layouts[0])
    title_slide.shapes.title.text = title
    if len(title_slide.placeholders) > 1:
        title_slide.placeholders[1].text = "Erstellt mit NotebookLM-Klon"

    bullet_layout = prs.slide_layouts[1]
    for slide_data in slides:
        slide = prs.slides.add_slide(bullet_layout)
        slide.shapes.title.text = slide_data.get("title", "")

        body = slide.placeholders[1].text_frame
        body.clear()
        bullets = slide_data.get("bullets", [])
        for i, bullet in enumerate(bullets):
            paragraph = body.paragraphs[0] if i == 0 else body.add_paragraph()
            paragraph.text = bullet
            paragraph.level = 0
            paragraph.font.size = Pt(18)

    if not slides:
        blank = prs.slides.add_slide(prs.slide_layouts[6])
        textbox = blank.shapes.add_textbox(Inches(1), Inches(1), Inches(8), Inches(1))
        textbox.text_frame.text = "Keine Inhalte verfügbar."

    buffer = io.BytesIO()
    prs.save(buffer)
    return buffer.getvalue()
