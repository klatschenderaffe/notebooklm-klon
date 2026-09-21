import pytest

from app.services.chunking import chunk_text


def test_empty_text_returns_no_chunks() -> None:
    assert chunk_text("", chunk_size=100, overlap=10) == []


def test_short_text_returns_single_chunk() -> None:
    assert chunk_text("Hallo Welt", chunk_size=100, overlap=10) == ["Hallo Welt"]


def test_long_text_is_split_into_overlapping_chunks() -> None:
    text = "Wort " * 500
    chunks = chunk_text(text, chunk_size=200, overlap=50)

    assert len(chunks) > 1
    assert all(len(chunk) <= 200 for chunk in chunks)
    assert "".join(chunks[0][-10:]) in text


def test_overlap_must_be_smaller_than_chunk_size() -> None:
    with pytest.raises(ValueError):
        chunk_text("irrelevant", chunk_size=50, overlap=50)


def test_no_chunk_is_empty() -> None:
    text = "Absatz eins.\n\nAbsatz zwei.\n\n\n\nAbsatz drei nach vielen Leerzeilen."
    chunks = chunk_text(text, chunk_size=20, overlap=5)
    assert all(chunk.strip() for chunk in chunks)


def test_link_list_without_blank_lines_does_not_produce_near_duplicate_chunks() -> None:
    """Regression test: live gefunden -- ein Markdown-Abschnitt aus Listeneinträgen
    ohne Leerzeilen dazwischen (z.B. eine Quellen-/Linkliste) ließ rfind(" ", ...) eine
    Grenze knapp hinter `start` finden. Der Chunk schrumpfte dadurch auf wenige
    Zeichen und `start` rückte pro Durchlauf nur um 1 Zeichen vor -- bei einer echten
    ~150 Zeichen langen Restlänge entstanden so 17 Fast-Duplikat-Chunks statt eines
    einzigen sauberen Blocks."""
    intro = "Text davor. " * 100  # füllt den ersten Chunk regulär auf
    link_list = "\n".join(f"- [Quelle {i}](https://example.com/quelle-{i})" for i in range(5))
    text = intro + "\n\n" + link_list

    chunks = chunk_text(text, chunk_size=1200, overlap=150)

    tiny_chunks = [c for c in chunks if len(c) < 50]
    assert not tiny_chunks, f"Erwartete keine winzigen Fast-Duplikate, gefunden: {tiny_chunks}"
