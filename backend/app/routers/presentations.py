import io

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.schemas import PresentationRequest
from app.services import vector_store
from app.services.design import validate_design
from app.services.gemini_client import generate_presentation_outline
from app.services.presentation import build_presentation

router = APIRouter(prefix="/presentations", tags=["presentations"])


@router.post("")
def create_presentation(request: PresentationRequest) -> StreamingResponse:
    chunks = vector_store.chunks_for_sources(request.source_ids)
    if not chunks:
        raise HTTPException(status_code=422, detail="Keine Quellen für die Präsentation gefunden")

    outline = generate_presentation_outline(
        request.topic,
        [c["content"] for c in chunks],
        design_description=request.design_description,
        tone=request.tone,
        slide_count_hint=request.slide_count_hint,
    )
    design = validate_design(outline.get("design"))
    slides = outline.get("slides", [])

    pptx_bytes = build_presentation(outline.get("title", request.topic), slides, design)

    return StreamingResponse(
        io.BytesIO(pptx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": 'attachment; filename="praesentation.pptx"'},
    )
