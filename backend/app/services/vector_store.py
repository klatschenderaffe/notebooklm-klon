from typing import Any, cast

from app.services.supabase_client import get_client


def insert_source(
    source_id: str, notebook_id: str, filename: str, file_type: str, storage_path: str
) -> dict[str, Any]:
    response = (
        get_client()
        .table("sources")
        .insert(
            {
                "id": source_id,
                "notebook_id": notebook_id,
                "filename": filename,
                "file_type": file_type,
                "storage_path": storage_path,
            }
        )
        .execute()
    )
    return cast(dict[str, Any], response.data[0])


def insert_chunks(source_id: str, chunks: list[str], embeddings: list[list[float]]) -> None:
    rows: list[dict[str, Any]] = [
        {"source_id": source_id, "chunk_index": i, "content": chunk, "embedding": embedding}
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings, strict=True))
    ]
    if rows:
        get_client().table("chunks").insert(rows).execute()


def list_sources(notebook_id: str) -> list[dict[str, Any]]:
    response = (
        get_client()
        .table("sources")
        .select("*")
        .eq("notebook_id", notebook_id)
        .order("created_at", desc=True)
        .execute()
    )
    return cast(list[dict[str, Any]], response.data)


def get_source(notebook_id: str, source_id: str) -> dict[str, Any] | None:
    response = (
        get_client()
        .table("sources")
        .select("*")
        .eq("id", source_id)
        .eq("notebook_id", notebook_id)
        .execute()
    )
    return cast(dict[str, Any], response.data[0]) if response.data else None


def delete_source(notebook_id: str, source_id: str) -> None:
    get_client().table("sources").delete().eq("id", source_id).eq(
        "notebook_id", notebook_id
    ).execute()


def similarity_search(
    notebook_id: str, query_embedding: list[float], match_count: int = 6
) -> list[dict[str, Any]]:
    response = (
        get_client()
        .rpc(
            "match_chunks",
            {
                "query_embedding": query_embedding,
                "target_notebook_id": notebook_id,
                "match_count": match_count,
            },
        )
        .execute()
    )
    return cast(list[dict[str, Any]], response.data)


def chunks_for_sources(notebook_id: str, source_ids: list[str] | None) -> list[dict[str, Any]]:
    sources_query = get_client().table("sources").select("id").eq("notebook_id", notebook_id)
    if source_ids:
        sources_query = sources_query.in_("id", source_ids)
    source_rows = cast(list[dict[str, Any]], sources_query.execute().data)
    notebook_source_ids = [row["id"] for row in source_rows]
    if not notebook_source_ids:
        return []

    chunks_query = (
        get_client()
        .table("chunks")
        .select("content, source_id")
        .in_("source_id", notebook_source_ids)
        .order("chunk_index")
    )
    return cast(list[dict[str, Any]], chunks_query.execute().data)
