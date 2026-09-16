from typing import Any, cast

from app.services.supabase_client import get_client


def insert_source(
    source_id: str, filename: str, file_type: str, storage_path: str
) -> dict[str, Any]:
    response = (
        get_client()
        .table("sources")
        .insert(
            {
                "id": source_id,
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


def list_sources() -> list[dict[str, Any]]:
    response = get_client().table("sources").select("*").order("created_at", desc=True).execute()
    return cast(list[dict[str, Any]], response.data)


def delete_source(source_id: str) -> None:
    get_client().table("sources").delete().eq("id", source_id).execute()


def similarity_search(query_embedding: list[float], match_count: int = 6) -> list[dict[str, Any]]:
    response = (
        get_client()
        .rpc("match_chunks", {"query_embedding": query_embedding, "match_count": match_count})
        .execute()
    )
    return cast(list[dict[str, Any]], response.data)


def chunks_for_sources(source_ids: list[str] | None) -> list[dict[str, Any]]:
    query = get_client().table("chunks").select("content, source_id").order("chunk_index")
    if source_ids:
        query = query.in_("source_id", source_ids)
    return cast(list[dict[str, Any]], query.execute().data)
