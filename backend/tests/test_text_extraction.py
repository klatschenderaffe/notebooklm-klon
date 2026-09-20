import pytest

from app.services.text_extraction import (
    UnsupportedFileTypeError,
    extract_text,
    file_type_from_filename,
)


def test_file_type_from_filename_pdf() -> None:
    assert file_type_from_filename("dokument.pdf") == "pdf"


def test_file_type_from_filename_markdown() -> None:
    assert file_type_from_filename("notizen.md") == "md"
    assert file_type_from_filename("notizen.markdown") == "md"


@pytest.mark.parametrize("filename", ["ton.mp3", "ton.wav", "ton.m4a", "ton.ogg", "bild.png"])
def test_file_type_from_filename_unsupported(filename: str) -> None:
    with pytest.raises(UnsupportedFileTypeError):
        file_type_from_filename(filename)


def test_extract_text_markdown() -> None:
    content = b"# Titel\n\nEin Absatz."
    assert extract_text("notizen.md", content) == "# Titel\n\nEin Absatz."


def test_extract_text_rejects_audio() -> None:
    with pytest.raises(UnsupportedFileTypeError):
        extract_text("ton.mp3", b"...")
