import ntpath
import posixpath
import re

from app.config import settings
from app.services.supabase_client import get_client

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
