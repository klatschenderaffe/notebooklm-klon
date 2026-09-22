import io

from pypdf import PdfReader

SUPPORTED_EXTENSIONS = {".pdf", ".md", ".markdown"}


class UnsupportedFileTypeError(ValueError):
    pass


def file_type_from_filename(filename: str) -> str:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return "pdf"
    if lower.endswith(".md") or lower.endswith(".markdown"):
        return "md"
    raise UnsupportedFileTypeError(f"Nicht unterstützter Dateityp: {filename}")


def extract_text(filename: str, content: bytes) -> str:
    """Nur für Dateitypen, deren Text ohne externen API-Call extrahierbar ist (PDF,
    Markdown)."""
    file_type = file_type_from_filename(filename)
    if file_type == "pdf":
        return _extract_pdf_text(content)
    # Windows-1252/Latin-1-kodierte .md-Dateien (z.B. aus älteren oder Windows-Editoren)
    # lassen decode("utf-8") sonst mit einer rohen UnicodeDecodeError crashen, die bis
    # zum generischen 500-Handler durchschlägt, statt dem Nutzer zu sagen, dass seine
    # Datei das Problem ist.
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"Datei hat ungültiges Encoding, erwartet wird UTF-8: {filename}") from exc


def _extract_pdf_text(content: bytes) -> str:
    reader = PdfReader(io.BytesIO(content))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages).strip()
