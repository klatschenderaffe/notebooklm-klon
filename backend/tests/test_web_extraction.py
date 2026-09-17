import pytest

import app.services.web_extraction as web_extraction
from app.services.web_extraction import UrlExtractionError, extract_url_content


def test_extract_url_content_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(web_extraction.trafilatura, "fetch_url", lambda url: "<html>...</html>")
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
    monkeypatch.setattr(web_extraction.trafilatura, "fetch_url", lambda url: None)

    with pytest.raises(UrlExtractionError):
        extract_url_content("https://does-not-exist.invalid")


def test_extract_url_content_no_text_found(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(web_extraction.trafilatura, "fetch_url", lambda url: "<html></html>")
    monkeypatch.setattr(web_extraction.trafilatura, "extract", lambda html, favor_recall=True: None)

    with pytest.raises(UrlExtractionError):
        extract_url_content("https://example.org/leer")


def test_extract_url_content_falls_back_to_url_as_title(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(web_extraction.trafilatura, "fetch_url", lambda url: "<html>...</html>")
    monkeypatch.setattr(
        web_extraction.trafilatura, "extract", lambda html, favor_recall=True: "Text"
    )
    monkeypatch.setattr(web_extraction.trafilatura, "extract_metadata", lambda html: None)

    title, _text = extract_url_content("https://example.org/ohne-titel")

    assert title == "https://example.org/ohne-titel"
