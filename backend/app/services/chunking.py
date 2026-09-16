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

    while start < text_length:
        end = min(start + chunk_size, text_length)
        if end < text_length:
            boundary = text.rfind("\n\n", start, end)
            if boundary == -1:
                boundary = text.rfind(" ", start, end)
            if boundary > start:
                end = boundary

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break
        start = max(end - overlap, start + 1)

    return chunks
