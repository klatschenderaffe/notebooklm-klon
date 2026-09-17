import io
import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.auth import get_current_user_id
from app.schemas import PresentationOut, PresentationRequest
from app.services import history_store, storage, vector_store
from app.services.design import validate_design
from app.services.gemini_client import generate_presentation_outline
from app.services.notebooks_store import require_owned_notebook_id
from app.services.presentation import build_presentation

router = APIRouter(prefix="/notebooks/{notebook_id}/presentations", tags=["presentations"])

PPTX_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.presentationml.presentation"


@router.get("", response_model=list[PresentationOut])
def list_presentations(notebook_id: str = Depends(require_owned_notebook_id)) -> list[dict]:
    return history_store.list_presentations(notebook_id)


@router.get("/{presentation_id}/download")
def download_presentation(
    presentation_id: str, notebook_id: str = Depends(require_owned_notebook_id)
) -> StreamingResponse:
    presentation = history_store.get_presentation(notebook_id, presentation_id)
    if presentation is None:
        raise HTTPException(status_code=404, detail="Präsentation nicht gefunden")

    pptx_bytes = storage.download_presentation_file(presentation["storage_path"])
    filename = f"{presentation['title']}.pptx"
    return StreamingResponse(
        io.BytesIO(pptx_bytes),
        media_type=PPTX_CONTENT_TYPE,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("")
def create_presentation(
    request: PresentationRequest,
    notebook_id: str = Depends(require_owned_notebook_id),
    user_id: str = Depends(get_current_user_id),
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
    title = outline.get("title", request.topic)

    pptx_bytes = build_presentation(title, slides, design)

    presentation_id = str(uuid.uuid4())
    storage_path = storage.upload_presentation_file(
        user_id, notebook_id, presentation_id, pptx_bytes
    )
    history_store.insert_presentation(notebook_id, title, request.topic, storage_path, design)

    return StreamingResponse(
        io.BytesIO(pptx_bytes),
        media_type=PPTX_CONTENT_TYPE,
        headers={"Content-Disposition": f'attachment; filename="{title}.pptx"'},
    )
