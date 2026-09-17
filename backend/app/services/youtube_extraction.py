import re

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)

VIDEO_ID_PATTERNS = [
    r"(?:v=|youtu\.be/|embed/|shorts/)([A-Za-z0-9_-]{11})",
]


class YoutubeExtractionError(ValueError):
    pass


def extract_video_id(url: str) -> str:
    for pattern in VIDEO_ID_PATTERNS:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise YoutubeExtractionError(f"Keine gültige YouTube-Video-ID in der URL gefunden: {url}")


def extract_youtube_transcript(url: str) -> tuple[str, str]:
    """Lädt das Transkript eines YouTube-Videos. Gibt (title, text) zurück — YouTube
    liefert über diese Bibliothek keinen Videotitel ohne zusätzlichen API-Key, daher wird
    die Video-ID als Platzhaltertitel verwendet."""
    video_id = extract_video_id(url)

    try:
        transcript = YouTubeTranscriptApi().fetch(video_id, languages=["de", "en"])
    except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable) as exc:
        raise YoutubeExtractionError(
            f"Kein Transkript für dieses Video verfügbar: {exc}"
        ) from exc

    text = "\n".join(snippet.text for snippet in transcript)
    if not text.strip():
        raise YoutubeExtractionError("Transkript ist leer")

    title = f"YouTube-Video {video_id}"
    return title, text
