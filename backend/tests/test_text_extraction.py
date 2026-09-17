import pytest

from app.services.text_extraction import (
    UnsupportedFileTypeError,
    audio_mime_type_from_filename,
    extract_text,
    file_type_from_filename,
)


def test_file_type_from_filename_pdf() -> None:
    assert file_type_from_filename("dokument.pdf") == "pdf"


def test_file_type_from_filename_markdown() -> None:
    assert file_type_from_filename("notizen.md") == "md"
    assert file_type_from_filename("notizen.markdown") == "md"


@pytest.mark.parametrize("filename", ["ton.mp3", "ton.wav", "ton.m4a", "ton.ogg"])
def test_file_type_from_filename_audio(filename: str) -> None:
    assert file_type_from_filename(filename) == "audio"


def test_file_type_from_filename_unsupported() -> None:
    with pytest.raises(UnsupportedFileTypeError):
        file_type_from_filename("bild.png")


def test_extract_text_markdown() -> None:
    content = b"# Titel\n\nEin Absatz."
    assert extract_text("notizen.md", content) == "# Titel\n\nEin Absatz."


def test_extract_text_rejects_audio() -> None:
    with pytest.raises(UnsupportedFileTypeError):
        extract_text("ton.mp3", b"...")


@pytest.mark.parametrize(
    ("filename", "expected_mime"),
    [
        ("ton.mp3", "audio/mpeg"),
        ("ton.wav", "audio/wav"),
        ("ton.m4a", "audio/mp4"),
        ("ton.ogg", "audio/ogg"),
    ],
)
def test_audio_mime_type_from_filename(filename: str, expected_mime: str) -> None:
    assert audio_mime_type_from_filename(filename) == expected_mime


def test_audio_mime_type_from_filename_rejects_non_audio() -> None:
    with pytest.raises(UnsupportedFileTypeError):
        audio_mime_type_from_filename("dokument.pdf")
