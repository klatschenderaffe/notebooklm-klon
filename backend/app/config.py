from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    gemini_api_key: str = ""
    gemini_chat_model: str = "gemini-3.6-flash"
    gemini_embedding_model: str = "gemini-embedding-2"
    gemini_embedding_dimensions: int = 768

    supabase_url: str = ""
    supabase_service_key: str = ""
    supabase_storage_bucket: str = "sources"
    supabase_presentations_bucket: str = "presentations"
    # Nur nötig, falls das Supabase-Projekt (noch) legacy HS256-JWTs signiert statt der
    # neueren asymmetrischen Signing Keys (JWKS) — siehe app/auth.py.
    supabase_jwt_secret: str = ""

    allowed_origins: str = "http://localhost:5173"

    chunk_size_chars: int = 1200
    chunk_overlap_chars: int = 150
    max_upload_size_bytes: int = 20 * 1024 * 1024

    # Mindest-Kosinus-Ähnlichkeit (0-1), ab der ein Chunk als relevant genug gilt, um als
    # Chat-Kontext/Zitat verwendet zu werden. match_chunks liefert sonst immer bis zu
    # match_count Treffer zurück, auch wenn kein einziger davon thematisch passt (z.B. bei
    # wenigen Quellen im Notebook) — kalibriert an echten Testdaten: ein tatsächlich
    # relevanter Chunk lag bei ~0.81, ein komplett themenfremder bei ~0.53.
    chat_similarity_threshold: float = 0.6


settings = Settings()
