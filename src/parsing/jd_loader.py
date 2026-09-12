"""Extract a deterministic requirement fixture from an uploaded JD."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from src.matching.normalization import ALIASES, extract_skill_mentions
from src.parsing.text_normalizer import normalize_text


RELATED_SKILLS = {
    "Node.js": ["Express.js", "REST API", "FastAPI", "Spring Boot"],
    "React": ["React Native", "Vue.js", "Angular"],
    "SQL": ["PostgreSQL", "MySQL", "SQLite"],
}


def extract_jd_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        try:
            import fitz
        except ImportError as error:
            raise RuntimeError("JD PDF support requires pymupdf") from error
        with fitz.open(path) as document:
            return normalize_text("\n".join(page.get_text("text") for page in document))
    if suffix == ".docx":
        try:
            from docx import Document
        except ImportError as error:
            raise RuntimeError("JD DOCX support requires python-docx") from error
        document = Document(path)
        return normalize_text("\n".join(paragraph.text for paragraph in document.paragraphs))
    return normalize_text(path.read_text(encoding="utf-8"))


def extract_requirements(text: str) -> dict[str, Any]:
    skills = extract_skill_mentions(text)
    requirements = []
    seen = set()
    for skill in skills:
        if skill in seen:
            continue
        seen.add(skill)
        importance = infer_importance(text, skill)
        requirements.append(
            {
                "requirement_id": f"req_{len(requirements) + 1:02d}",
                "canonical_name": skill,
                "category": "technical_skill",
                "importance": importance,
                "weight": {"required": 2.0, "preferred": 1.0, "nice_to_have": 0.5}[importance],
                "aliases": [alias for alias, canonical in ALIASES.items() if canonical == skill],
                "related_skills": RELATED_SKILLS.get(skill, []),
                "source_text": find_source_text(text, skill),
                "evidence_expectations": [f"evidence of {skill} use"],
            }
        )
    return {"job_title": first_nonempty_line(text) or "Uploaded Job Description", "requirements": requirements}


def infer_importance(text: str, skill: str) -> str:
    for line in text.splitlines():
        if re.search(rf"(?<!\w){re.escape(skill)}(?!\w)", line, re.IGNORECASE):
            lowered = line.lower()
            if any(marker in lowered for marker in ("must", "required", "mandatory")):
                return "required"
            if any(marker in lowered for marker in ("preferred", "plus", "bonus")):
                return "nice_to_have"
    return "preferred"


def find_source_text(text: str, skill: str) -> str:
    for line in text.splitlines():
        if re.search(rf"(?<!\w){re.escape(skill)}(?!\w)", line, re.IGNORECASE):
            return line
    return skill


def first_nonempty_line(text: str) -> str:
    return next((line.strip() for line in text.splitlines() if line.strip()), "")
