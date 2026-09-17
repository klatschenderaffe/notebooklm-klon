import pytest
from youtube_transcript_api._errors import TranscriptsDisabled

import app.services.youtube_extraction as youtube_extraction
from app.services.youtube_extraction import (
    YoutubeExtractionError,
    extract_video_id,
    extract_youtube_transcript,
)


@pytest.mark.parametrize(
    "url",
    [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "https://www.youtube.com/shorts/dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=30s",
    ],
)
def test_extract_video_id_recognizes_common_url_formats(url: str) -> None:
    assert extract_video_id(url) == "dQw4w9WgXcQ"


def test_extract_video_id_rejects_non_youtube_url() -> None:
    with pytest.raises(YoutubeExtractionError):
        extract_video_id("https://example.org/not-youtube")


class _FakeSnippet:
    def __init__(self, text: str) -> None:
        self.text = text


def test_extract_youtube_transcript_success(monkeypatch: pytest.MonkeyPatch) -> None:
    class _FakeApi:
        def fetch(self, video_id: str, languages: list[str]) -> list[_FakeSnippet]:
            assert video_id == "dQw4w9WgXcQ"
            return [_FakeSnippet("Erste Zeile."), _FakeSnippet("Zweite Zeile.")]

    monkeypatch.setattr(youtube_extraction, "YouTubeTranscriptApi", _FakeApi)

    title, text = extract_youtube_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    assert "dQw4w9WgXcQ" in title
    assert text == "Erste Zeile.\nZweite Zeile."


def test_extract_youtube_transcript_disabled_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    class _FakeApi:
        def fetch(self, video_id: str, languages: list[str]) -> list[_FakeSnippet]:
            raise TranscriptsDisabled(video_id)

    monkeypatch.setattr(youtube_extraction, "YouTubeTranscriptApi", _FakeApi)

    with pytest.raises(YoutubeExtractionError):
        extract_youtube_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
