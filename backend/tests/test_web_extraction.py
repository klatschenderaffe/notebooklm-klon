import socket

import pytest

import app.services.web_extraction as web_extraction
from app.services.web_extraction import UrlExtractionError, extract_url_content


def _stub_public_dns(monkeypatch: pytest.MonkeyPatch, ip: str = "93.184.216.34") -> None:
    """Simuliert eine Hostname-Auflösung auf eine öffentliche IP, damit Tests nicht auf
    echte DNS/Netzwerk-Zugriffe angewiesen sind (siehe socket.getaddrinfo-Aufruf in
    _validate_public_url)."""
    monkeypatch.setattr(
        web_extraction.socket,
        "getaddrinfo",
        lambda host, port: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, 0))],
    )


def test_extract_url_content_success(monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_public_dns(monkeypatch)
    monkeypatch.setattr(
        web_extraction.trafilatura, "fetch_url", lambda url, config=None: "<html>...</html>"
    )
    monkeypatch.setattr(
        web_extraction.trafilatura, "extract", lambda html, favor_recall=True: "Der Haupttext."
    )
    monkeypatch.setattr(
        web_extraction.trafilatura,
        "extract_metadata",
        lambda html: type("M", (), {"title": "Seitentitel"})(),
    )

    title, text = extract_url_content("https://example.org/artikel")

    assert title == "Seitentitel"
    assert text == "Der Haupttext."


def test_extract_url_content_fetch_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_public_dns(monkeypatch)
    monkeypatch.setattr(web_extraction.trafilatura, "fetch_url", lambda url, config=None: None)

    with pytest.raises(UrlExtractionError):
        extract_url_content("https://does-not-exist.invalid")


def test_extract_url_content_no_text_found(monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_public_dns(monkeypatch)
    monkeypatch.setattr(
        web_extraction.trafilatura, "fetch_url", lambda url, config=None: "<html></html>"
    )
    monkeypatch.setattr(web_extraction.trafilatura, "extract", lambda html, favor_recall=True: None)

    with pytest.raises(UrlExtractionError):
        extract_url_content("https://example.org/leer")


def test_extract_url_content_falls_back_to_url_as_title(monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_public_dns(monkeypatch)
    monkeypatch.setattr(
        web_extraction.trafilatura, "fetch_url", lambda url, config=None: "<html>...</html>"
    )
    monkeypatch.setattr(
        web_extraction.trafilatura, "extract", lambda html, favor_recall=True: "Text"
    )
    monkeypatch.setattr(web_extraction.trafilatura, "extract_metadata", lambda html: None)

    title, _text = extract_url_content("https://example.org/ohne-titel")

    assert title == "https://example.org/ohne-titel"


def test_extract_url_content_truncates_very_long_text(monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_public_dns(monkeypatch)
    monkeypatch.setattr(web_extraction.settings, "max_extracted_url_text_chars", 10)
    monkeypatch.setattr(
        web_extraction.trafilatura, "fetch_url", lambda url, config=None: "<html>...</html>"
    )
    monkeypatch.setattr(
        web_extraction.trafilatura,
        "extract",
        lambda html, favor_recall=True: "0123456789ABCDEF",
    )
    monkeypatch.setattr(web_extraction.trafilatura, "extract_metadata", lambda html: None)

    _title, text = extract_url_content("https://example.org/lang")

    assert text == "0123456789"


@pytest.mark.parametrize(
    "url",
    [
        "http://localhost/",
        "http://127.0.0.1/",
        "http://[::1]/",
        "ftp://example.org/",
        "not-a-url",
    ],
)
def test_validate_public_url_rejects_obviously_unsafe_urls(url: str) -> None:
    with pytest.raises(UrlExtractionError):
        web_extraction._validate_public_url(url)


@pytest.mark.parametrize(
    "ip",
    [
        "127.0.0.1",  # Loopback
        "10.0.0.5",  # Privates Netz (RFC 1918)
        "172.16.0.1",  # Privates Netz (RFC 1918)
        "192.168.1.1",  # Privates Netz (RFC 1918)
        "169.254.169.254",  # Link-Local, u.a. AWS/GCP Cloud-Metadata-Endpunkt
        "0.0.0.0",  # Reserved
    ],
)
def test_validate_public_url_rejects_hostnames_resolving_to_private_ips(
    monkeypatch: pytest.MonkeyPatch, ip: str
) -> None:
    """Deckt den DNS-Rebinding-artigen Fall ab: der Hostname selbst sieht harmlos aus,
    löst aber zur Request-Zeit auf eine private/interne IP auf."""
    monkeypatch.setattr(
        web_extraction.socket,
        "getaddrinfo",
        lambda host, port: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, 0))],
    )

    with pytest.raises(UrlExtractionError):
        web_extraction._validate_public_url("http://looks-public.example.com/")


def test_validate_public_url_rejects_if_any_resolved_ip_is_private(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ein Hostname kann auf mehrere IPs auflösen (z.B. Round-Robin-DNS) — es reicht,
    wenn eine davon privat/intern ist, um die URL abzulehnen."""
    monkeypatch.setattr(
        web_extraction.socket,
        "getaddrinfo",
        lambda host, port: [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 0)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.1", 0)),
        ],
    )

    with pytest.raises(UrlExtractionError):
        web_extraction._validate_public_url("http://mixed-dns.example.com/")


def test_validate_public_url_accepts_public_ip(monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_public_dns(monkeypatch)
    web_extraction._validate_public_url("https://example.org/artikel")


def test_validate_public_url_rejects_unresolvable_hostname(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _raise(host: str, port: None) -> list:
        raise socket.gaierror("Name or service not known")

    monkeypatch.setattr(web_extraction.socket, "getaddrinfo", _raise)

    with pytest.raises(UrlExtractionError):
        web_extraction._validate_public_url("https://does-not-exist.invalid/")
