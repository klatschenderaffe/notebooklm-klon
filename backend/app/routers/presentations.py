import io

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.schemas import PresentationRequest
from app.services import vector_store
from app.services.design import validate_design
from app.services.gemini_client import generate_presentation_outline
from app.services.notebooks_store import require_owned_notebook_id
from app.services.presentation import build_presentation

router = APIRouter(prefix="/notebooks/{notebook_id}/presentations", tags=["presentations"])


@router.post("")
def create_presentation(
    request: PresentationRequest, notebook_id: str = Depends(require_owned_notebook_id)
) -> StreamingResponse:
    chunks = vector_store.chunks_for_sources(notebook_id, request.source_ids)
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
