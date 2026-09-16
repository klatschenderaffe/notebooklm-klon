from app.config import settings
from app.services.supabase_client import get_client


def upload_source_file(source_id: str, filename: str, content: bytes) -> str:
    storage_path = f"{source_id}/{filename}"
    get_client().storage.from_(settings.supabase_storage_bucket).upload(storage_path, content)
    return storage_path
