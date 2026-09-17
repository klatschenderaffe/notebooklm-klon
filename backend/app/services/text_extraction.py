import io

from pypdf import PdfReader

SUPPORTED_EXTENSIONS = {".pdf", ".md", ".markdown", ".mp3", ".wav", ".m4a", ".ogg"}

AUDIO_MIME_TYPES = {
    "mp3": "audio/mpeg",
    "wav": "audio/wav",
    "m4a": "audio/mp4",
    "ogg": "audio/ogg",
}


class UnsupportedFileTypeError(ValueError):
    pass


def file_type_from_filename(filename: str) -> str:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return "pdf"
    if lower.endswith(".md") or lower.endswith(".markdown"):
        return "md"
    for ext in AUDIO_MIME_TYPES:
        if lower.endswith(f".{ext}"):
            return "audio"
    raise UnsupportedFileTypeError(f"Nicht unterstützter Dateityp: {filename}")


def audio_mime_type_from_filename(filename: str) -> str:
    lower = filename.lower()
    for ext, mime_type in AUDIO_MIME_TYPES.items():
        if lower.endswith(f".{ext}"):
            return mime_type
    raise UnsupportedFileTypeError(f"Nicht unterstützter Audio-Dateityp: {filename}")


def extract_text(filename: str, content: bytes) -> str:
    """Nur für Dateitypen, deren Text ohne externen API-Call extrahierbar ist (PDF,
    Markdown). Audio-Transkription läuft separat über gemini_client.transcribe_audio,
    da sie einen Gemini-API-Aufruf erfordert."""
    file_type = file_type_from_filename(filename)
    if file_type == "pdf":
        return _extract_pdf_text(content)
    if file_type == "md":
        return content.decode("utf-8")
    raise UnsupportedFileTypeError(
        f"extract_text unterstützt keine Audio-Dateien direkt: {filename}"
    )


def _extract_pdf_text(content: bytes) -> str:
    reader = PdfReader(io.BytesIO(content))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages).strip()
