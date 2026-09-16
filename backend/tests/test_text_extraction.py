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


def test_file_type_from_filename_unsupported() -> None:
    with pytest.raises(UnsupportedFileTypeError):
        file_type_from_filename("bild.png")


def test_extract_text_markdown() -> None:
    content = b"# Titel\n\nEin Absatz."
    assert extract_text("notizen.md", content) == "# Titel\n\nEin Absatz."
