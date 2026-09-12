"""Flag potentially narrow or exclusionary JD phrasing for review."""

from __future__ import annotations

import re
from typing import Any


PATTERNS = {
    "age_or_recency": (
        r"\b(?:young|recent graduate|fresh graduate|digital native|under \d+|\d+\s*[- ]year[- ]old)\b",
        "Potential age or graduation-recency bias",
    ),
    "unnecessary_culture": (
        r"\b(?:culture fit|native speaker|rockstar|ninja|hacker|work hard play hard)\b",
        "Potentially subjective or exclusionary culture wording",
    ),
    "overly_narrow_background": (
        r"\b(?:top[- ]tier college only|ivy league only|must be from|only candidates from)\b",
        "Potentially overly narrow education or background requirement",
    ),
    "gendered_language": (
        r"\b(?:he|she|manpower|guys|aggressive|dominant)\b",
        "Potentially gendered wording",
    ),
}


def flag_jd_bias(text: str) -> list[dict[str, Any]]:
    findings = []
    for category, (pattern, message) in PATTERNS.items():
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            start = max(0, match.start() - 60)
            end = min(len(text), match.end() + 60)
            findings.append(
                {
                    "category": category,
                    "message": message,
                    "phrase": match.group(0),
                    "context": text[start:end].replace("\n", " "),
                }
            )
    return findings
