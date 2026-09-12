"""Extract a deterministic requirement fixture from an uploaded JD."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from src.matching.normalization import ALIASES, extract_skill_mentions
from src.parsing.text_normalizer import normalize_text


RELATED_SKILLS = {
    "Node.js": ["Express.js", "REST API", "FastAPI", "NestJS", "JavaScript", "TypeScript"],
    "React": ["React Native", "Vue.js", "Angular", "Next.js", "Redux", "JavaScript", "TypeScript"],
    "React Native": ["React", "Flutter", "Android SDK", "iOS"],
    "Flutter": ["Dart", "React Native", "Android SDK"],
    "Python": ["Django", "FastAPI", "Flask", "Pandas", "NumPy", "PyTorch"],
    "Java": ["Spring Boot", "Kotlin", "Android SDK"],
    "Kotlin": ["Java", "Android SDK"],
    "SQL": ["PostgreSQL", "MySQL", "SQLite", "MongoDB", "Redis"],
    "PostgreSQL": ["SQL", "MySQL", "SQLite"],
    "MySQL": ["SQL", "PostgreSQL"],
    "MongoDB": ["SQL", "Redis"],
    "Docker": ["Kubernetes", "CI/CD", "AWS", "Linux"],
    "Kubernetes": ["Docker", "CI/CD", "AWS", "Cloud"],
    "AWS": ["Azure", "Google Cloud", "Docker", "Kubernetes"],
    "Git": ["GitHub", "GitLab", "CI/CD"],
    "FastAPI": ["Python", "Flask", "REST API", "Django"],
    "Django": ["Python", "Flask", "FastAPI"],
    "Spring Boot": ["Java", "REST API", "Microservices"],
    "Express.js": ["Node.js", "JavaScript", "REST API"],
    "REST API": ["GraphQL", "FastAPI", "Express.js", "Microservices"],
    "TypeScript": ["JavaScript", "React", "Node.js"],
    "JavaScript": ["TypeScript", "React", "Node.js"],
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
    requirements = []
    seen: dict[str, dict[str, Any]] = {}
    current_section = "general"

    for line in text.splitlines():
        trimmed = line.strip()
        if not trimmed:
            continue
        is_bullet = trimmed.startswith(("-", "*", "•", "+")) or bool(re.match(r"^\d+[\.\)]", trimmed))
        words = trimmed.split()
        if not is_bullet and len(words) <= 5:
            lowered_heading = re.sub(r"[^a-zA-Z ]", " ", trimmed).lower().strip()
            if any(h in lowered_heading for h in ("must have", "minimum qualification", "basic qualification", "mandatory requirement", "required skill", "requirements")):
                current_section = "required"
                continue
            elif any(h in lowered_heading for h in ("good to have", "preferred qualification", "nice to have", "desired qualification", "bonus point", "plus")):
                current_section = "preferred"
                continue
            elif any(h in lowered_heading for h in ("responsibilities", "about the role", "soft skills", "benefits", "overview")):
                current_section = "general"
                continue

        line_skills = extract_skill_mentions(trimmed)
        for skill in line_skills:
            importance = "preferred"
            if current_section == "required":
                importance = "required"
            elif current_section == "preferred":
                importance = "nice_to_have"
            else:
                lowered_line = trimmed.lower()
                marker_line = lowered_line.replace("-", " ")
                if any(m in marker_line for m in ("must", "required", "mandatory", "essential", "minimum", "need to have")):
                    importance = "required"
                elif any(m in marker_line for m in ("preferred", "plus", "bonus", "nice to have", "good to have", "optional")):
                    importance = "nice_to_have"
                else:
                    importance = "preferred"

            if skill in seen:
                if importance == "required" and seen[skill]["importance"] != "required":
                    seen[skill]["importance"] = "required"
                    seen[skill]["weight"] = 2.0
                    seen[skill]["source_text"] = trimmed
                continue

            weight_map = {"required": 2.0, "preferred": 1.0, "nice_to_have": 0.5}
            item = {
                "requirement_id": f"req_{len(requirements) + 1:02d}",
                "canonical_name": skill,
                "category": "technical_skill",
                "importance": importance,
                "weight": weight_map.get(importance, 1.0),
                "aliases": [alias for alias, canonical in ALIASES.items() if canonical == skill],
                "related_skills": RELATED_SKILLS.get(skill, []),
                "source_text": trimmed,
                "evidence_expectations": [f"evidence of {skill} use"],
            }
            requirements.append(item)
            seen[skill] = item

    requirements = collapse_requirement_groups(requirements, text)
    for index, requirement in enumerate(requirements, start=1):
        requirement["requirement_id"] = f"req_{index:02d}"

    title = detect_job_title(text)
    return {"job_title": title, "requirements": requirements}


def collapse_requirement_groups(
    requirements: list[dict[str, Any]], text: str
) -> list[dict[str, Any]]:
    """Preserve the JD's alternatives instead of making each one a separate gate.

    A phrase such as "SQL or NoSQL (MySQL, PostgreSQL, MongoDB)" means one
    database competency, not four mandatory technologies. The same applies to
    Git/GitHub and the JD's "at least one frontend framework" wording.
    """
    normalized = text.lower()
    grouped = list(requirements)

    def replace(
        members: set[str],
        canonical_name: str,
        importance: str,
        acceptable_skills: list[str] | None = None,
        text_patterns: list[str] | None = None,
    ) -> None:
        nonlocal grouped
        positions = [index for index, item in enumerate(grouped) if item["canonical_name"] in members]
        if not positions:
            return
        first = min(positions)
        source_items = [grouped[index] for index in positions]
        grouped = [item for item in grouped if item["canonical_name"] not in members]
        weight = {"required": 2.0, "preferred": 1.0, "nice_to_have": 0.5}[importance]
        group = {
            "requirement_id": "",
            "canonical_name": canonical_name,
            "category": "technical_skill",
            "importance": importance,
            "weight": weight,
            "aliases": [],
            "related_skills": [],
            "acceptable_skills": acceptable_skills or [],
            "text_patterns": text_patterns or [],
            "source_text": source_items[0]["source_text"],
            "evidence_expectations": [f"evidence of {canonical_name}"],
        }
        grouped.insert(first, group)

    if "modern frontend framework" in normalized:
        replace(
            {"React", "Next.js", "Angular", "Vue.js"},
            "Modern frontend framework",
            "required",
            ["React", "Next.js", "Angular", "Vue.js"],
        )
    if "node.js and express" in normalized or "node.js/express" in normalized:
        # Node.js is the runtime requirement; Express is its required framework
        # in this JD, rather than a substitute for Node itself.
        replace({"Express.js", "NestJS"}, "Node.js backend framework", "required", ["Express.js", "NestJS"])
    if "es6" in normalized:
        # TypeScript, React-family work, and Node.js all require practical
        # JavaScript fluency; do not reject an otherwise full-stack candidate
        # solely because their resume names the adjacent technology instead.
        replace(
            {"JavaScript", "TypeScript"},
            "JavaScript (ES6+)",
            "required",
            ["JavaScript", "TypeScript", "Node.js", "React", "Next.js", "Angular", "Vue.js"],
        )
    if "sql or nosql" in normalized or "relational and nosql" in normalized:
        replace(
            {"SQL", "PostgreSQL", "MySQL", "MongoDB", "SQLite", "Redis"},
            "SQL or NoSQL database",
            "required",
            ["PostgreSQL", "MySQL", "MongoDB", "SQLite", "Redis"],
        )
    if "git/github" in normalized or "git / github" in normalized:
        replace({"Git", "GitHub", "GitLab"}, "Git version control", "required", ["Git", "GitHub", "GitLab"])
    if "computer science" in normalized and ("related field" in normalized or "information technology" in normalized):
        group = {
            "requirement_id": "",
            "canonical_name": "CS/IT-related degree",
            "category": "education",
            "importance": "required",
            "weight": 2.0,
            "aliases": [],
            "related_skills": [],
            "acceptable_skills": [],
            "text_patterns": [
                r"computer science",
                r"information technology",
                r"\bb\.?\s*tech\b.*(?:computer|information)",
                r"\bb\.?\s*e\b.*(?:computer|information)",
                r"\bb\.?\s*c\.?\s*a\.?",
            ],
            "source_text": "CS/IT-related degree requirement",
            "evidence_expectations": ["evidence of a CS, IT, or related degree"],
        }
        first_required = next((index for index, item in enumerate(grouped) if item["importance"] == "required"), len(grouped))
        grouped.insert(first_required, group)

    if "cloud basics" in normalized:
        replace({"AWS", "Azure", "Google Cloud"}, "Cloud fundamentals", "nice_to_have", ["AWS", "Azure", "Google Cloud"])
    if "testing frameworks" in normalized:
        replace({"Jest", "Mocha"}, "Testing framework", "nice_to_have", ["Jest", "Mocha"])
    if "agile/scrum" in normalized:
        replace({"Agile", "Scrum"}, "Agile/Scrum", "nice_to_have", ["Agile", "Scrum"])

    return grouped


def detect_job_title(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines[:5]:
        if any(role in line.lower() for role in ("developer", "engineer", "intern", "manager", "architect", "lead", "designer", "consultant")):
            return line.split("|")[0].strip()
    return lines[0] if lines else "Uploaded Job Description"


def infer_importance(text: str, skill: str) -> str:
    current_section = "general"
    for line in text.splitlines():
        trimmed = line.strip().lower()
        if any(h in trimmed for h in ("must have", "minimum qualification", "basic qualification", "mandatory requirement", "required skill", "requirements:")):
            current_section = "required"
        elif any(h in trimmed for h in ("preferred qualification", "nice to have", "desired qualification", "bonus point", "good to have", "plus:")):
            current_section = "preferred"

        if re.search(rf"(?<!\w){re.escape(skill)}(?!\w)", line, re.IGNORECASE):
            lowered = line.lower()
            marker_line = lowered.replace("-", " ")
            if any(marker in marker_line for marker in ("must", "required", "mandatory", "essential", "minimum", "need to have")):
                return "required"
            if any(marker in marker_line for marker in ("preferred", "plus", "bonus", "nice to have", "good to have", "optional")):
                return "nice_to_have"
            if current_section == "required":
                return "required"
            if current_section == "preferred":
                return "nice_to_have"
    return "preferred"


def find_source_text(text: str, skill: str) -> str:
    for line in text.splitlines():
        if re.search(rf"(?<!\w){re.escape(skill)}(?!\w)", line, re.IGNORECASE):
            return line
    return skill


def first_nonempty_line(text: str) -> str:
    return next((line.strip() for line in text.splitlines() if line.strip()), "")
