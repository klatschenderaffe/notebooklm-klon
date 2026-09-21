import ipaddress
import socket
from urllib.parse import urlparse

import trafilatura
from trafilatura.settings import use_config

from app.config import settings


class UrlExtractionError(ValueError):
    pass


def _validate_public_url(url: str) -> None:
    """Blockt SSRF-Versuche, BEVOR trafilatura.fetch_url() die URL abruft.

    Diese Quelle wird von jedem authentifizierten Nutzer frei eingegeben, und der
    Server (nicht der Browser des Nutzers) führt den Request aus — ohne Prüfung könnte
    ein Nutzer den Server dazu bringen, interne Dienste anzusprechen (z.B.
    http://localhost:6379, http://10.0.0.5/admin) oder Cloud-Metadata-Endpunkte
    auszulesen (http://169.254.169.254/... liefert bei AWS/GCP oft IAM-Credentials).

    Wichtig: Es wird der tatsächlich AUFGELÖSTE Hostname geprüft (via
    socket.getaddrinfo), nicht nur der String in der URL. Ein Angreifer könnte sonst
    einen Hostnamen verwenden, der öffentlich aussieht, aber zur Request-Zeit auf eine
    private IP aufgelöst wird (DNS-Rebinding-artiges Vorgehen) — eine reine
    String-Prüfung auf "localhost"/"127.0.0.1" im Hostnamen würde das nicht erkennen.
    Ein Hostname kann außerdem auf mehrere IPs auflösen (z.B. Round-Robin-DNS); daher
    werden ALLE von getaddrinfo gelieferten Adressen geprüft, nicht nur die erste.
    """
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise UrlExtractionError(f"Nicht unterstütztes URL-Schema: {url}")
    if not parsed.hostname:
        raise UrlExtractionError(f"Ungültige URL: {url}")

    try:
        addr_infos = socket.getaddrinfo(parsed.hostname, None)
    except OSError as exc:
        raise UrlExtractionError(f"Hostname konnte nicht aufgelöst werden: {url}") from exc

    for family, _type, _proto, _canonname, sockaddr in addr_infos:
        ip_str = sockaddr[0]
        ip = ipaddress.ip_address(ip_str)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            raise UrlExtractionError(
                f"URL zeigt auf eine nicht öffentlich erreichbare Adresse: {url}"
            )


def extract_url_content(url: str) -> tuple[str, str]:
    """Lädt eine Webseite und extrahiert Haupttext + Titel. Gibt (title, text) zurück."""
    # Bewusst akzeptiertes Restrisiko: _validate_public_url() löst den Hostnamen EINMAL
    # auf und prüft die dabei gelieferten IPs, aber trafilatura.fetch_url() löst den
    # Hostnamen für den tatsächlichen Abruf gleich danach intern selbst nochmal auf
    # (TOCTOU/DNS-Rebinding) -- zwischen Prüfung und Abruf könnte sich die DNS-Antwort
    # ändern, z.B. wenn ein Angreifer eine Domain mit sehr kurzer TTL betreibt, die bei
    # der ersten Auflösung eine öffentliche IP und bei der zweiten (durch fetch_url())
    # eine private/interne IP liefert.
    #
    # Vollständig beheben ließe sich das nur durch IP-Pinning: die bereits validierte IP
    # direkt für den HTTP-Request verwenden statt den Hostnamen erneut auflösen zu
    # lassen. trafilatura.fetch_url() unterstützt das nicht ohne größeren Eigenbau (z.B.
    # eine eigene Session mit gepinntem Connection-Adapter statt der eingebauten
    # Abruf-Logik), was für dieses Projekt nicht im Verhältnis zum Risiko steht: der
    # Angreifer müsste eine von ihm kontrollierte Domain mit sehr kurzer DNS-TTL
    # betreiben UND einen Nutzer dazu bringen, genau diese URL als Quelle hinzuzufügen
    # UND das Timing zwischen den beiden Auflösungen exakt treffen. Dieses Restrisiko
    # wird daher bewusst in Kauf genommen, nicht übersehen.
    _validate_public_url(url)

    # Explizites, kürzeres Timeout statt trafilatura-Default (30s, siehe
    # trafilatura/settings.cfg) — sonst blockiert eine sehr langsame Zielseite den
    # einzigen Worker-Thread des Backends unnötig lange. config.getint() ist der
    # Mechanismus, über den fetch_url() den Timeout tatsächlich an die zugrunde
    # liegende HTTP-Bibliothek weitergibt (siehe trafilatura/downloads.py).
    download_config = use_config()
    download_config.set("DEFAULT", "DOWNLOAD_TIMEOUT", str(settings.url_extraction_timeout_seconds))

    downloaded = trafilatura.fetch_url(url, config=download_config)
    if downloaded is None:
        raise UrlExtractionError(f"Seite konnte nicht geladen werden: {url}")

    text = trafilatura.extract(downloaded, favor_recall=True)
    if not text or not text.strip():
        raise UrlExtractionError(f"Kein Text auf der Seite gefunden: {url}")

    # Grobe Obergrenze statt unbegrenzter Chunk-/Embedding-Anzahl für eine einzige,
    # sehr große Webseite (siehe max_extracted_url_text_chars in app/config.py). Text
    # wird abgeschnitten, nicht die Extraktion verworfen — ein Teil des Inhalts ist
    # weiterhin nützlicher als eine harte Ablehnung der Quelle.
    text = text[: settings.max_extracted_url_text_chars]

    metadata = trafilatura.extract_metadata(downloaded)
    title = (metadata.title if metadata and metadata.title else None) or url

    return title, text
