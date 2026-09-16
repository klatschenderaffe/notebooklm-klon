import re
from typing import Any

HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")

# Fonts, die auf PowerPoint, Google Slides, Keynote und LibreOffice zuverlässig verfügbar
# sind. Gemini wird angewiesen, nur aus dieser Liste zu wählen; validate_design() fängt
# ungültige Werte trotzdem sicherheitshalber ab.
ALLOWED_FONTS = [
    "Arial",
    "Calibri",
    "Georgia",
    "Verdana",
    "Trebuchet MS",
    "Garamond",
    "Tahoma",
    "Century Gothic",
]

DEFAULT_DESIGN = {
    "background_color": "#FFFFFF",
    "accent_color": "#16A34A",
    "text_color": "#1A1A1A",
    "heading_font": "Calibri",
    "body_font": "Calibri",
}


def validate_design(design: dict[str, Any] | None) -> dict[str, str]:
    """Übernimmt gültige Felder aus dem von Gemini gelieferten Design, ersetzt ungültige
    oder fehlende Felder einzeln durch den Default-Wert (kein Alles-oder-nichts-Fallback)."""
    design = design or {}
    result = dict(DEFAULT_DESIGN)

    for field in ("background_color", "accent_color", "text_color"):
        value = design.get(field)
        if isinstance(value, str) and HEX_COLOR_RE.match(value):
            result[field] = value

    for field in ("heading_font", "body_font"):
        value = design.get(field)
        if isinstance(value, str) and value in ALLOWED_FONTS:
            result[field] = value

    return result
