import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile

from app.auth import get_current_user_id
from app.config import settings
from app.schemas import SourceOut
from app.services import storage, vector_store
from app.services.chunking import chunk_text
from app.services.gemini_client import embed_texts
from app.services.notebooks_store import require_owned_notebook_id
from app.services.text_extraction import (
    UnsupportedFileTypeError,
    extract_text,
    file_type_from_filename,
)

router = APIRouter(prefix="/notebooks/{notebook_id}/sources", tags=["sources"])


@router.get("", response_model=list[SourceOut])
def list_sources(notebook_id: str = Depends(require_owned_notebook_id)) -> list[dict]:
    return vector_store.list_sources(notebook_id)


@router.post("", response_model=SourceOut, status_code=201)
async def upload_source(
    file: UploadFile,
    notebook_id: str = Depends(require_owned_notebook_id),
    user_id: str = Depends(get_current_user_id),
) -> dict:
    if file.filename is None:
        raise HTTPException(status_code=422, detail="Dateiname fehlt")

    try:
        file_type = file_type_from_filename(file.filename)
    except UnsupportedFileTypeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    content = await file.read()
    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(status_code=413, detail="Datei zu groß")

    text = extract_text(file.filename, content)
    if not text.strip():
        raise HTTPException(
            status_code=422, detail="Aus der Datei konnte kein Text extrahiert werden"
        )

    chunks = chunk_text(text, settings.chunk_size_chars, settings.chunk_overlap_chars)
    embeddings = embed_texts(chunks, task_type="RETRIEVAL_DOCUMENT")

    source_id = str(uuid.uuid4())
    storage_path = storage.upload_source_file(
        user_id, notebook_id, source_id, file.filename, content, file_type
    )
    source = vector_store.insert_source(
        source_id, notebook_id, file.filename, file_type, storage_path
    )
    vector_store.insert_chunks(source_id, chunks, embeddings)

    return source


@router.delete("/{source_id}", status_code=204)
def delete_source(
    source_id: str, notebook_id: str = Depends(require_owned_notebook_id)
) -> None:
    source = vector_store.get_source(notebook_id, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Quelle nicht gefunden")
    storage.delete_source_file(source["storage_path"])
    vector_store.delete_source(notebook_id, source_id)
