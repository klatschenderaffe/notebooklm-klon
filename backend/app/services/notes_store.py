from typing import Any, cast

from app.services.supabase_client import get_client


def insert_note(source_id: str, content: str) -> dict[str, Any]:
    response = (
        get_client()
        .table("notes")
        .insert({"source_id": source_id, "content": content})
        .execute()
    )
    return cast(dict[str, Any], response.data[0])


def list_notes(source_id: str) -> list[dict[str, Any]]:
    response = (
        get_client()
        .table("notes")
        .select("*")
        .eq("source_id", source_id)
        .order("created_at")
        .execute()
    )
    return cast(list[dict[str, Any]], response.data)


def delete_note(source_id: str, note_id: str) -> bool:
    response = (
        get_client()
        .table("notes")
        .delete()
        .eq("id", note_id)
        .eq("source_id", source_id)
        .execute()
    )
    return bool(response.data)
