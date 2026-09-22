from fastapi import APIRouter, Depends, HTTPException

from app.schemas import NoteCreate, NoteOut
from app.services import notes_store, vector_store
from app.services.notebooks_store import require_owned_notebook_id

router = APIRouter(prefix="/notebooks/{notebook_id}/sources/{source_id}/notes", tags=["notes"])


def require_owned_source_id(
    source_id: str, notebook_id: str = Depends(require_owned_notebook_id)
) -> str:
    """FastAPI-Dependency: prüft zusätzlich zur Notebook-Eigentümerschaft, dass die
    Quelle existiert und zu diesem Notebook gehört, bevor auf ihre Notizen zugegriffen
    werden darf."""
    if vector_store.get_source(notebook_id, source_id) is None:
        raise HTTPException(status_code=404, detail="Quelle nicht gefunden")
    return source_id


@router.get("", response_model=list[NoteOut])
def list_notes(source_id: str = Depends(require_owned_source_id)) -> list[dict]:
    return notes_store.list_notes(source_id)


@router.post("", response_model=NoteOut, status_code=201)
def add_note(request: NoteCreate, source_id: str = Depends(require_owned_source_id)) -> dict:
    if not request.content.strip():
        raise HTTPException(status_code=422, detail="Notiz darf nicht leer sein")
    return notes_store.insert_note(source_id, request.content)


@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: str, source_id: str = Depends(require_owned_source_id)) -> None:
    if not notes_store.delete_note(source_id, note_id):
        raise HTTPException(status_code=404, detail="Notiz nicht gefunden")
