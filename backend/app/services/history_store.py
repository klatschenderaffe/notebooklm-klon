from typing import Any, cast

from app.services.supabase_client import get_client


def insert_chat_message(
    notebook_id: str, role: str, content: str, citations: list[dict[str, Any]]
) -> dict[str, Any]:
    response = (
        get_client()
        .table("chat_messages")
        .insert(
            {
                "notebook_id": notebook_id,
                "role": role,
                "content": content,
                "citations": citations,
            }
        )
        .execute()
    )
    return cast(dict[str, Any], response.data[0])


def list_chat_messages(notebook_id: str) -> list[dict[str, Any]]:
    response = (
        get_client()
        .table("chat_messages")
        .select("*")
        .eq("notebook_id", notebook_id)
        .order("created_at")
        .execute()
    )
    return cast(list[dict[str, Any]], response.data)


def insert_presentation(
    notebook_id: str, title: str, topic: str, storage_path: str, design: dict[str, str]
) -> dict[str, Any]:
    response = (
        get_client()
        .table("presentations")
        .insert(
            {
                "notebook_id": notebook_id,
                "title": title,
                "topic": topic,
                "storage_path": storage_path,
                "design": design,
            }
        )
        .execute()
    )
    return cast(dict[str, Any], response.data[0])


def list_presentations(notebook_id: str) -> list[dict[str, Any]]:
    response = (
        get_client()
        .table("presentations")
        .select("*")
        .eq("notebook_id", notebook_id)
        .order("created_at", desc=True)
        .execute()
    )
    return cast(list[dict[str, Any]], response.data)


def get_presentation(notebook_id: str, presentation_id: str) -> dict[str, Any] | None:
    response = (
        get_client()
        .table("presentations")
        .select("*")
        .eq("id", presentation_id)
        .eq("notebook_id", notebook_id)
        .execute()
    )
    return cast(dict[str, Any], response.data[0]) if response.data else None
