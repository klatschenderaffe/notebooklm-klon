from functools import lru_cache

from app.config import settings
from supabase import Client, create_client


@lru_cache
def get_client() -> Client:
    return create_client(settings.supabase_url, settings.supabase_service_key)
