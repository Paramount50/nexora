"""Deterministic cleanup shared by every resume input format."""

from __future__ import annotations

import re
import unicodedata


UNICODE_REPLACEMENTS = str.maketrans(
    {
        "\u2010": "-",
        "\u2011": "-",
        "\u2012": "-",
        "\u2013": "-",
        "\u2014": "-",
        "\u2212": "-",
        "\u2022": "-",
        "\u25cf": "-",
        "\u00a0": " ",
    }
)


def normalize_text(value: str) -> str:
    """Normalize formatting noise while preserving meaningful line breaks."""
    value = unicodedata.normalize("NFKC", value).translate(UNICODE_REPLACEMENTS)
    lines = []
    for line in value.splitlines():
        line = re.sub(r"[ \t]+", " ", line).strip()
        line = re.sub(r"^[-*]\s+", "- ", line)
        if line:
            lines.append(line)
    return "\n".join(lines)


def normalize_value(value: str) -> str:
    return normalize_text(value).replace("\n", " ").strip()
