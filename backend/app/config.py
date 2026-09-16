from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    gemini_api_key: str = ""
    gemini_chat_model: str = "gemini-3.8-flash"
    gemini_embedding_model: str = "gemini-embedding-2"
    gemini_embedding_dimensions: int = 768

    supabase_url: str = ""
    supabase_service_key: str = ""
    supabase_storage_bucket: str = "sources"

    allowed_origins: str = "http://localhost:5173"

    chunk_size_chars: int = 1200
    chunk_overlap_chars: int = 150
    max_upload_size_bytes: int = 20 * 1024 * 1024


settings = Settings()
