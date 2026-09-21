import logging
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

# Fällt zurück auf diesen Wert, wenn SENTRY_TRACES_SAMPLE_RATE nicht als Zahl parsbar ist
# (siehe sentry_traces_sample_rate-Validator unten).
DEFAULT_SENTRY_TRACES_SAMPLE_RATE = 1.0


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

    # Timeout für den Abruf einer URL-Quelle (Sekunden). trafilatura.fetch_url() hat
    # standardmäßig 30s Timeout (siehe trafilatura/settings.cfg) — das würde den
    # einzigen Worker-Thread des Backends bei einer sehr langsamen Zielseite lange
    # blockieren. Bewusst kürzer als der Default, da Nutzer beim Hinzufügen einer
    # URL-Quelle synchron auf die Antwort warten.
    url_extraction_timeout_seconds: int = 10

    # Obergrenze für den aus einer URL extrahierten Text (Zeichen), BEVOR er gechunkt
    # und eingebettet wird. Ohne dieses Limit kann eine einzelne, sehr große Webseite
    # (z.B. eine lange Doku-Seite oder ein Datendump) unbegrenzt viele Chunks und damit
    # Gemini-Embedding-Calls erzeugen — Risiko einer Kontingent-Erschöpfung durch eine
    # einzige Quelle. Der Text wird bei Überschreitung sauber abgeschnitten statt die
    # Quelle ganz abzulehnen, analog zu max_upload_size_bytes für Datei-Uploads.
    max_extracted_url_text_chars: int = 200_000

    # Mindest-Kosinus-Ähnlichkeit (0-1), ab der ein Chunk als relevant genug gilt, um als
    # Chat-Kontext/Zitat verwendet zu werden. match_chunks liefert sonst immer bis zu
    # match_count Treffer zurück, auch wenn kein einziger davon thematisch passt (z.B. bei
    # wenigen Quellen im Notebook). Ursprünglich an einem einzigen Beispielpaar auf 0.6
    # kalibriert (relevant ~0.81, themenfremd ~0.53) — mit mehr echten Testdaten (Frage zu
    # "Wombats" bei einer zusätzlichen "Quokka"-Wikipedia-Quelle im selben Notebook) zeigte
    # sich, dass thematisch verwandte, aber inhaltlich irrelevante Treffer (beides
    # australische Beuteltiere) auf 0.62-0.67 kommen können, oberhalb der alten Schwelle.
    # Auf 0.7 angehoben, da der tatsächlich relevante Treffer in diesem Test bei 0.77 lag.
    chat_similarity_threshold: float = 0.7

    # Sentry Error-Tracking (Phase 5, DevOps-Hardening). Bei leerem DSN (Standard, z.B.
    # lokale Entwicklung ohne Sentry-Account) wird Sentry gar nicht erst initialisiert —
    # siehe app/main.py.
    sentry_dsn: str = ""
    environment: str = "development"

    # Anteil der Requests (0.0-1.0), für die Sentry Performance-Traces erfasst. Aktuell
    # bewusst hoch (1.0 = 100%) für die Staging-/Demo-Phase ohne echten Produktivtraffic,
    # um beim Aufbau möglichst vollständige Traces zu bekommen. Bei echtem
    # Produktivbetrieb mit nennenswertem Traffic sollte dieser Wert auf z.B. 0.1-0.2
    # reduziert werden, um im kostenlosen Sentry-Kontingent (5.000.000 Spans/Monat) zu
    # bleiben.
    sentry_traces_sample_rate: float = DEFAULT_SENTRY_TRACES_SAMPLE_RATE

    @field_validator("sentry_traces_sample_rate", mode="before")
    @classmethod
    def _parse_sentry_traces_sample_rate(cls, value: Any) -> Any:
        """Robuster Fallback statt Crash beim Settings-Laden.

        Ein nicht-parsbarer Wert (z.B. leerer String, weil ein Feld im Render-Dashboard
        versehentlich leer gelassen wurde) würde pydantic sonst eine ValidationError
        werfen lassen -- und zwar beim Modul-Import (`settings = Settings()` unten), also
        BEVOR app/main.py's try/except um _init_sentry() überhaupt greifen kann. Das
        würde den kompletten Backend-Start verhindern, nicht nur Sentry. Analog zum
        Frontend-Pattern in frontend/src/main.tsx (Number(...) mit
        Number.isFinite-Fallback), das aus demselben Grund existiert.

        Gültige, aber außerhalb von [0, 1] liegende Werte (z.B. 5.0) werden hier bewusst
        durchgereicht -- die validiert sentry_sdk selbst (is_valid_sample_rate) und
        deaktiviert Sampling bei ungültigem Wert nur mit einer Warnung, ohne zu crashen.
        """
        if value is None or isinstance(value, int | float):
            return value
        try:
            return float(value)
        except (TypeError, ValueError):
            logger.warning(
                "SENTRY_TRACES_SAMPLE_RATE=%r ist nicht als Zahl parsbar, "
                "verwende Standardwert %s.",
                value,
                DEFAULT_SENTRY_TRACES_SAMPLE_RATE,
            )
            return DEFAULT_SENTRY_TRACES_SAMPLE_RATE


settings = Settings()
