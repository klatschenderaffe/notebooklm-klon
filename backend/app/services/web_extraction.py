import trafilatura


class UrlExtractionError(ValueError):
    pass


def extract_url_content(url: str) -> tuple[str, str]:
    """Lädt eine Webseite und extrahiert Haupttext + Titel. Gibt (title, text) zurück."""
    downloaded = trafilatura.fetch_url(url)
    if downloaded is None:
        raise UrlExtractionError(f"Seite konnte nicht geladen werden: {url}")

    text = trafilatura.extract(downloaded, favor_recall=True)
    if not text or not text.strip():
        raise UrlExtractionError(f"Kein Text auf der Seite gefunden: {url}")

    metadata = trafilatura.extract_metadata(downloaded)
    title = (metadata.title if metadata and metadata.title else None) or url

    return title, text
