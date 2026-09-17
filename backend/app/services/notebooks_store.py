from typing import Any, cast

from fastapi import Depends, HTTPException

from app.auth import get_current_user_id
from app.services.supabase_client import get_client


def create_notebook(user_id: str, name: str) -> dict[str, Any]:
    response = (
        get_client().table("notebooks").insert({"user_id": user_id, "name": name}).execute()
    )
    return cast(dict[str, Any], response.data[0])


def list_notebooks(user_id: str) -> list[dict[str, Any]]:
    response = (
        get_client()
        .table("notebooks")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return cast(list[dict[str, Any]], response.data)


def rename_notebook(user_id: str, notebook_id: str, name: str) -> dict[str, Any]:
    response = (
        get_client()
        .table("notebooks")
        .update({"name": name})
        .eq("id", notebook_id)
        .eq("user_id", user_id)
        .execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Notebook nicht gefunden")
    return cast(dict[str, Any], response.data[0])


def delete_notebook(user_id: str, notebook_id: str) -> None:
    response = (
        get_client()
        .table("notebooks")
        .delete()
        .eq("id", notebook_id)
        .eq("user_id", user_id)
        .execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Notebook nicht gefunden")


def get_owned_notebook(user_id: str, notebook_id: str) -> dict[str, Any]:
    """Prüft, dass das Notebook existiert und dem aktuellen Nutzer gehört. Als FastAPI-
    Dependency-Baustein in den notebook-scoped Routern verwendet (sources/chat/
    presentations), damit jede Operation dort automatisch die Eigentümerschaft prüft."""
    response = (
        get_client()
        .table("notebooks")
        .select("*")
        .eq("id", notebook_id)
        .eq("user_id", user_id)
        .execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Notebook nicht gefunden")
    return cast(dict[str, Any], response.data[0])


def list_source_storage_paths(notebook_id: str) -> list[str]:
    """Storage-Pfade aller Quellen eines Notebooks, um sie vor dem Löschen des Notebooks
    auch im Storage-Bucket zu entfernen statt sie zu verwaisen."""
    response = (
        get_client()
        .table("sources")
        .select("storage_path")
        .eq("notebook_id", notebook_id)
        .execute()
    )
    rows = cast(list[dict[str, Any]], response.data)
    return [row["storage_path"] for row in rows]


def list_presentation_storage_paths(notebook_id: str) -> list[str]:
    """Wie list_source_storage_paths, aber für generierte Präsentationen (separater
    Storage-Bucket)."""
    response = (
        get_client()
        .table("presentations")
        .select("storage_path")
        .eq("notebook_id", notebook_id)
        .execute()
    )
    rows = cast(list[dict[str, Any]], response.data)
    return [row["storage_path"] for row in rows]


def require_owned_notebook_id(
    notebook_id: str, user_id: str = Depends(get_current_user_id)
) -> str:
    """FastAPI-Dependency für notebook-scoped Router (sources/chat/presentations):
    prüft Auth + Eigentümerschaft in einem Schritt, gibt die geprüfte notebook_id zurück."""
    get_owned_notebook(user_id, notebook_id)
    return notebook_id
