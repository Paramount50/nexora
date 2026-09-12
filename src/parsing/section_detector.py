"""Detect common resume sections in flattened extracted text."""

from __future__ import annotations

import re


SECTION_ALIASES = {
    "summary": {"summary", "professional summary", "profile", "objective", "about me"},
    "skills": {"skills", "technical skills", "technical proficiencies", "technologies", "tools"},
    "experience": {"experience", "work experience", "professional experience", "internship", "employment"},
    "projects": {"projects", "personal projects", "academic projects"},
    "education": {"education", "academic background", "qualifications"},
    "certifications": {"certifications", "certificates", "licenses"},
    "achievements": {"achievements", "awards", "honors"},
    "extracurricular": {"extracurricular", "activities", "leadership", "volunteering"},
}

ALIASES_TO_SECTION = {
    alias: section for section, aliases in SECTION_ALIASES.items() for alias in aliases
}


def detect_sections(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {section: [] for section in SECTION_ALIASES}
    sections["other"] = []
    current = "other"

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        heading = normalize_heading(line)
        if heading in ALIASES_TO_SECTION:
            current = ALIASES_TO_SECTION[heading]
            continue
        sections[current].append(line)

    return {section: values for section, values in sections.items() if values}


def normalize_heading(value: str) -> str:
    value = re.sub(r"[^a-zA-Z ]", " ", value).lower()
    return re.sub(r"\s+", " ", value).strip()
