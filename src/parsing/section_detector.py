"""Detect common resume sections in flattened extracted text."""

from __future__ import annotations

import re


SECTION_ALIASES = {
    "summary": {
        "summary", "professional summary", "executive summary", "profile",
        "career objective", "objective", "about me", "personal statement",
        "overview", "introduction", "background",
    },
    "skills": {
        "skills", "technical skills", "technical proficiencies", "technical expertise",
        "core competencies", "technologies", "tools", "skills and tools",
        "programming languages", "frameworks", "tech stack", "competencies",
        "skills proficiencies", "areas of expertise",
    },
    "experience": {
        "experience", "work experience", "professional experience", "employment history",
        "employment", "work history", "internship", "internships", "career history",
        "relevant experience", "professional background", "experience history",
    },
    "projects": {
        "projects", "personal projects", "academic projects", "key projects",
        "notable projects", "open source projects", "portfolio", "project work",
        "selected projects", "technical projects",
    },
    "education": {
        "education", "academic background", "academic qualifications", "qualifications",
        "academic credentials", "educational background", "degrees", "academics",
    },
    "certifications": {
        "certifications", "certificates", "licenses", "certifications and courses",
        "courses", "professional certifications", "training", "credentials",
    },
    "achievements": {
        "achievements", "awards", "honors", "key achievements", "accomplishments",
        "publications", "recognition",
    },
    "extracurricular": {
        "extracurricular", "extracurricular activities", "activities", "leadership",
        "volunteering", "volunteer experience", "affiliations", "interests",
    },
}

ALIASES_TO_SECTION = {
    alias: section for section, aliases in SECTION_ALIASES.items() for alias in aliases
}


def match_heading_section(heading: str) -> str | None:
    if not heading or len(heading) > 60:
        return None
    if heading in ALIASES_TO_SECTION:
        return ALIASES_TO_SECTION[heading]
    
    # Check parts separated by delimiters like |, /, &, and, -
    sub_parts = re.split(r"\s*(?:\||/|&|\band\b|-)\s*", heading)
    for part in sub_parts:
        part_norm = part.strip()
        if part_norm in ALIASES_TO_SECTION:
            return ALIASES_TO_SECTION[part_norm]
    
    # Check if any known alias is contained as a word boundary in short heading
    for alias, section in sorted(ALIASES_TO_SECTION.items(), key=lambda item: len(item[0]), reverse=True):
        if re.search(rf"\b{re.escape(alias)}\b", heading):
            return section
    return None


def detect_sections(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {section: [] for section in SECTION_ALIASES}
    sections["other"] = []
    current = "other"

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        heading = normalize_heading(line)
        matched_section = match_heading_section(heading)
        if matched_section:
            current = matched_section
            continue
        sections[current].append(line)

    return {section: values for section, values in sections.items() if values}


def normalize_heading(value: str) -> str:
    # Strip markdown symbols, numbering, colons, bullets, and separators from edges
    cleaned = re.sub(r"^[#\*\-•0-9.\s]+", "", value)
    cleaned = re.sub(r"[:\|\-_~*\s]+$", "", cleaned)
    cleaned = re.sub(r"[^a-zA-Z |/&-]", " ", cleaned).lower()
    return re.sub(r"\s+", " ", cleaned).strip()
