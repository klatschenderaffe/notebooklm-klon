from app.config import settings
from app.services.supabase_client import get_client

CONTENT_TYPES = {
    "pdf": "application/pdf",
    "md": "text/markdown",
}


def upload_source_file(
    user_id: str, notebook_id: str, source_id: str, filename: str, content: bytes, file_type: str
) -> str:
    storage_path = f"{user_id}/{notebook_id}/{source_id}/{filename}"
    content_type = CONTENT_TYPES[file_type]
    get_client().storage.from_(settings.supabase_storage_bucket).upload(
        storage_path, content, file_options={"content-type": content_type}
    )
    return storage_path


def delete_source_file(storage_path: str) -> None:
    get_client().storage.from_(settings.supabase_storage_bucket).remove([storage_path])


PRESENTATION_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.presentationml.presentation"
)


def upload_presentation_file(
    user_id: str, notebook_id: str, presentation_id: str, content: bytes
) -> str:
    storage_path = f"{user_id}/{notebook_id}/{presentation_id}.pptx"
    get_client().storage.from_(settings.supabase_presentations_bucket).upload(
        storage_path, content, file_options={"content-type": PRESENTATION_CONTENT_TYPE}
    )
    return storage_path


def download_presentation_file(storage_path: str) -> bytes:
    return bytes(
        get_client().storage.from_(settings.supabase_presentations_bucket).download(storage_path)
    )


def delete_presentation_file(storage_path: str) -> None:
    get_client().storage.from_(settings.supabase_presentations_bucket).remove([storage_path])
