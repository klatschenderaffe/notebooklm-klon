from fastapi import APIRouter, Depends

from app.auth import get_current_user_id
from app.schemas import NotebookCreate, NotebookOut, NotebookUpdate
from app.services import notebooks_store, storage

router = APIRouter(prefix="/notebooks", tags=["notebooks"])


@router.get("", response_model=list[NotebookOut])
def list_notebooks(user_id: str = Depends(get_current_user_id)) -> list[dict]:
    return notebooks_store.list_notebooks(user_id)


@router.post("", response_model=NotebookOut, status_code=201)
def create_notebook(
    body: NotebookCreate, user_id: str = Depends(get_current_user_id)
) -> dict:
    return notebooks_store.create_notebook(user_id, body.name)


@router.patch("/{notebook_id}", response_model=NotebookOut)
def rename_notebook(
    notebook_id: str, body: NotebookUpdate, user_id: str = Depends(get_current_user_id)
) -> dict:
    return notebooks_store.rename_notebook(user_id, notebook_id, body.name)


@router.delete("/{notebook_id}", status_code=204)
def delete_notebook(notebook_id: str, user_id: str = Depends(get_current_user_id)) -> None:
    notebooks_store.get_owned_notebook(user_id, notebook_id)
    for path in notebooks_store.list_source_storage_paths(notebook_id):
        storage.delete_source_file(path)
    for path in notebooks_store.list_presentation_storage_paths(notebook_id):
        storage.delete_presentation_file(path)
    notebooks_store.delete_notebook(user_id, notebook_id)
