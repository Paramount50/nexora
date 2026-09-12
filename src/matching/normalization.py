"""Conservative canonical skill and alias normalization."""

from __future__ import annotations

import re


ALIASES = {
    "javascript": "JavaScript",
    "js": "JavaScript",
    "react native": "React Native",
    "react.js": "React",
    "reactjs": "React",
    "react": "React",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "express.js": "Express.js",
    "express": "Express.js",
    "rest apis": "REST API",
    "rest api": "REST API",
    "restful api": "REST API",
    "python": "Python",
    "java": "Java",
    "sql": "SQL",
    "sqlite": "SQLite",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "git": "Git",
    "github": "GitHub",
    "docker": "Docker",
    "aws": "AWS",
    "azure": "Azure",
    "flutter": "Flutter",
    "firebase": "Firebase",
    "android sdk": "Android SDK",
    "kotlin": "Kotlin",
    "dart": "Dart",
}


def normalize_skill(value: str) -> str | None:
    normalized = re.sub(r"\s+", " ", value.strip().lower())
    return ALIASES.get(normalized)


def extract_skill_mentions(text: str) -> list[str]:
    normalized = text.lower()
    matches: list[str] = []
    occupied: list[tuple[int, int]] = []

    for alias, canonical in sorted(ALIASES.items(), key=lambda item: len(item[0]), reverse=True):
        for match in re.finditer(rf"(?<!\w){re.escape(alias)}(?!\w)", normalized):
            span = match.span()
            if any(span[0] < end and start < span[1] for start, end in occupied):
                continue
            occupied.append(span)
            if canonical not in matches:
                matches.append(canonical)

    return matches
