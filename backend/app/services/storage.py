import logging
import ntpath
import posixpath
import re
import time
from collections.abc import Callable

import httpx
from fastapi import HTTPException

from app.config import settings
from app.services.supabase_client import get_client

logger = logging.getLogger(__name__)

STORAGE_UNAVAILABLE_DETAIL = (
    "Speicher-Service ist momentan nicht erreichbar. Bitte versuche es später erneut."
)


# Live gefunden: ein Upload einer echten Quelle schlug nach genau den 20s
# Standard-Timeout der Supabase-Python-Bibliothek (ClientOptions.storage_client_timeout)
# mit einem ungefangenen httpx.ReadTimeout fehl -- landete als roher 500 beim Nutzer,
# obwohl das Embedding direkt davor bereits erfolgreich war. Analog zu
# gemini_client._call_with_retry: ein einzelner Retry fängt den häufigsten Fall (kurzer
# transienter Netzwerk-Hänger) ab, bevor eine Fehlermeldung beim Nutzer ankommt.
def _call_with_retry[T](fn: Callable[[], T], *, retry_delay_seconds: float = 1.5) -> T:
    try:
        return fn()
    except httpx.TimeoutException as exc:
        logger.warning(
            "Supabase-Storage-Timeout, wiederhole einmal nach %.1fs: %s",
            retry_delay_seconds,
            exc,
        )
        time.sleep(retry_delay_seconds)
        return fn()


# Live gefunden (Sentry): ein URL-Quellen-Titel wie "[Hiring] DevOps Engineer
# @Everlast Consulting GmbH" ließ den Supabase-Storage-Upload mit "Invalid key"
# fehlschlagen -- eckige Klammern und "@" sind zwar keine Pfad-Traversal-Zeichen (schon
# durch basename()/lstrip(".") abgedeckt), aber trotzdem keine gültigen Storage-Key-
# Zeichen. Statt jedes Mal ein neu gefundenes Sonderzeichen einzeln zu verbieten (fragil,
# nie vollständig), wird jetzt eine feste Erlaubnisliste durchgesetzt: alles außer
# Buchstaben/Ziffern/Leerzeichen/"-"/"_"/"." wird durch "_" ersetzt.
_UNSAFE_FILENAME_CHARS = re.compile(r"[^A-Za-z0-9 ._-]")

CONTENT_TYPES = {
    "pdf": "application/pdf",
    "md": "text/markdown",
    # URL-Quellen werden als extrahierter Text abgelegt, konsistent mit Markdown-Quellen.
    "url": "text/markdown",
}


def _sanitize_filename(filename: str) -> str:
    """Entfernt aus einem client-gelieferten Dateinamen alles, was ihn zu einem
    Pfad-Bestandteil statt eines reinen Dateinamens machen würde, BEVOR er in den
    Storage-Pfad eingebaut wird.

    filename kommt direkt vom Client (UploadFile.filename bzw. der extrahierte
    URL-Titel) und wird ungeprüft in f"{user_id}/{notebook_id}/{source_id}/{filename}"
    eingesetzt. Ohne diese Bereinigung könnte ein Dateiname wie "../../../etc/passwd"
    oder "..\\..\\config" den Storage-Pfad verlassen (Path Traversal). posixpath.basename
    UND ntpath.basename werden beide angewendet, da Supabase Storage selbst nur "/" als
    Trenner kennt, ein Client aber auch rückwärtsgerichtete Windows-Backslashes senden
    könnte, die sonst als normale Zeichen im "Dateinamen" landen würden. Null-Bytes
    werden separat entfernt, da sie in Dateinamen ohnehin nie sinnvoll sind und in
    manchen darunterliegenden C-Bibliotheken Strings vorzeitig abschneiden können.
    """
    cleaned = filename.replace("\x00", "")
    cleaned = ntpath.basename(cleaned)
    cleaned = posixpath.basename(cleaned)
    # Erlaubnisliste statt Verbotsliste -- deckt auch Zeichen ab, die kein Pfad-
    # Traversal-Risiko sind, aber trotzdem als Storage-Key ungültig sind (z.B. "[", "]",
    # "@", siehe Kommentar bei _UNSAFE_FILENAME_CHARS oben).
    cleaned = _UNSAFE_FILENAME_CHARS.sub("_", cleaned)
    # Führende Punkte (".", "..", "...") ergeben nach basename() zwar keinen
    # Verzeichnis-Anteil mehr, könnten aber z.B. versteckte Dateien erzeugen oder als
    # "." bzw. ".." komplett leer wirken -- daher zusätzlich entfernen.
    cleaned = cleaned.lstrip(".")
    # Ein Dateiname, der nur aus Leerzeichen besteht (z.B. "   " oder "  .pdf", das nach
    # dem Punkt-Stripping zu "  " würde), ist als Storage-Pfad-Segment technisch nicht
    # leer, aber praktisch unbrauchbar -- daher vor der Leerheitsprüfung strippen, damit
    # auch solche Fälle auf den "datei"-Fallback treffen.
    cleaned = cleaned.strip()
    return cleaned or "datei"


def upload_source_file(
    user_id: str, notebook_id: str, source_id: str, filename: str, content: bytes, file_type: str
) -> str:
    safe_filename = _sanitize_filename(filename)
    storage_path = f"{user_id}/{notebook_id}/{source_id}/{safe_filename}"
    content_type = CONTENT_TYPES[file_type]
    try:
        _call_with_retry(
            lambda: (
                get_client()
                .storage.from_(settings.supabase_storage_bucket)
                .upload(storage_path, content, file_options={"content-type": content_type})
            )
        )
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=503, detail=STORAGE_UNAVAILABLE_DETAIL) from exc
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
