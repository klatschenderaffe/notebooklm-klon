import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile

from app.auth import get_current_user_id
from app.config import settings
from app.schemas import SourceOut, UrlSourceRequest
from app.services import storage, vector_store
from app.services.chunking import chunk_text
from app.services.gemini_client import embed_texts
from app.services.notebooks_store import require_owned_notebook_id
from app.services.text_extraction import (
    UnsupportedFileTypeError,
    extract_text,
    file_type_from_filename,
)
from app.services.web_extraction import UrlExtractionError, extract_url_content

router = APIRouter(prefix="/notebooks/{notebook_id}/sources", tags=["sources"])
logger = logging.getLogger(__name__)


def _ingest_source(
    user_id: str,
    notebook_id: str,
    filename: str,
    file_type: str,
    raw_content: bytes,
    text: str,
) -> dict:
    """Gemeinsame Pipeline für alle Quellentypen (Datei-Upload, URL):
    chunken, einbetten, Original-Content im Storage ablegen, DB-Einträge anlegen.

    Supabase bietet keine Mehrtabellen-Transaktion über den REST-Client, daher wird
    Storage-Upload und DB-Insert hier manuell abgesichert: schlägt insert_chunks (oder
    ein Schritt danach) fehl, werden bereits angelegte Storage-Datei und Source-Zeile
    wieder entfernt, statt eine "leere" Quelle mit 0 Chunks zurückzulassen, die zwar in
    der Liste auftaucht, aber im Chat nie gefunden wird. Live aufgetreten: ein Bug in
    embed_texts ließ genau das passieren, bevor diese Absicherung existierte."""
    if not text.strip():
        raise HTTPException(
            status_code=422, detail="Aus der Quelle konnte kein Text extrahiert werden"
        )

    chunks = chunk_text(text, settings.chunk_size_chars, settings.chunk_overlap_chars)
    embeddings = embed_texts(chunks, task_type="RETRIEVAL_DOCUMENT")

    source_id = str(uuid.uuid4())
    storage_path = storage.upload_source_file(
        user_id, notebook_id, source_id, filename, raw_content, file_type
    )
    try:
        source = vector_store.insert_source(
            source_id, notebook_id, filename, file_type, storage_path
        )
        vector_store.insert_chunks(source_id, chunks, embeddings)
    except Exception:
        logger.exception(
            "Ingestion fehlgeschlagen nach Storage-Upload, räume auf: source_id=%s", source_id
        )
        storage.delete_source_file(storage_path)
        vector_store.delete_source(notebook_id, source_id)
        raise

    return source


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

    return _ingest_source(user_id, notebook_id, file.filename, file_type, content, text)


@router.post("/url", response_model=SourceOut, status_code=201)
def add_url_source(
    request: UrlSourceRequest,
    notebook_id: str = Depends(require_owned_notebook_id),
    user_id: str = Depends(get_current_user_id),
) -> dict:
    try:
        title, text = extract_url_content(request.url)
    except UrlExtractionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return _ingest_source(user_id, notebook_id, title, "url", text.encode("utf-8"), text)


@router.delete("/{source_id}", status_code=204)
def delete_source(
    source_id: str, notebook_id: str = Depends(require_owned_notebook_id)
) -> None:
    source = vector_store.get_source(notebook_id, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Quelle nicht gefunden")
    storage.delete_source_file(source["storage_path"])
    vector_store.delete_source(notebook_id, source_id)
