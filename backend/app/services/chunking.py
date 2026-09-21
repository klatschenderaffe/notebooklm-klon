def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Teilt Text in überlappende Chunks fester Zeichenlänge, bevorzugt an Absatzgrenzen."""
    text = text.strip()
    if not text:
        return []
    if overlap >= chunk_size:
        raise ValueError("overlap muss kleiner als chunk_size sein")

    chunks: list[str] = []
    start = 0
    text_length = len(text)
    # Live gefunden: eine Grenze (Leerzeile oder Leerzeichen), die nur knapp hinter
    # `start` liegt, ließ den Chunk auf wenige Zeichen schrumpfen und `start` dadurch
    # pro Durchlauf nur um 1 Zeichen vorrücken -- bei einer Markdown-Linkliste ohne
    # Leerzeilen zwischen den Einträgen entstanden so 17 Fast-Duplikat-Chunks statt
    # eines sauberen ~1200-Zeichen-Blocks. Eine gefundene Grenze wird deshalb nur noch
    # verwendet, wenn sie mindestens die Hälfte von chunk_size Fortschritt bringt --
    # sonst wird stattdessen hart bei chunk_size abgeschnitten.
    min_boundary_offset = chunk_size // 2

    while start < text_length:
        end = min(start + chunk_size, text_length)
        if end < text_length:
            boundary = text.rfind("\n\n", start, end)
            if boundary == -1:
                boundary = text.rfind(" ", start, end)
            if boundary > start + min_boundary_offset:
                end = boundary

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break
        start = max(end - overlap, start + 1)

    return chunks
