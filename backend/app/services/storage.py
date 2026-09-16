from app.config import settings
from app.services.supabase_client import get_client

CONTENT_TYPES = {
    "pdf": "application/pdf",
    "md": "text/markdown",
}


def upload_source_file(source_id: str, filename: str, content: bytes, file_type: str) -> str:
    storage_path = f"{source_id}/{filename}"
    content_type = CONTENT_TYPES[file_type]
    get_client().storage.from_(settings.supabase_storage_bucket).upload(
        storage_path, content, file_options={"content-type": content_type}
    )
    return storage_path
