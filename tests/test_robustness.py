from pathlib import Path

import pytest

from src.matching.normalization import extract_skill_mentions
from src.matching.ranker import rank_candidate
from src.parsing.resume_loader import load_resume, load_text_resume
from src.parsing.section_detector import detect_sections


REQUIREMENTS = [
    {
        "requirement_id": "req_node",
        "canonical_name": "Node.js",
        "importance": "required",
        "weight": 1.0,
        "related_skills": ["Express.js"],
    }
]


def test_malformed_pdf_fails_explicitly(tmp_path: Path) -> None:
    path = tmp_path / "broken.pdf"
    path.write_bytes(b"not a PDF")
    with pytest.raises(Exception):
        load_resume(path)


def test_missing_sections_are_preserved_as_other_text() -> None:
    sections = detect_sections("Candidate Name\nBuilt backend services with Node.js")
    assert sections["other"] == ["Candidate Name", "Built backend services with Node.js"]


def test_duplicate_skill_mentions_are_deduplicated() -> None:
    assert extract_skill_mentions("React, React, React.js") == ["React"]


def test_empty_resume_produces_no_evidence(tmp_path: Path) -> None:
    path = tmp_path / "empty.txt"
    path.write_text("", encoding="utf-8")
    candidate = load_text_resume(path)
    assert candidate["evidence"] == []


def test_no_evidence_candidate_fails_mandatory_requirement() -> None:
    result = rank_candidate(
        {"candidate_id": "empty", "candidate_name": "Empty", "evidence": []},
        REQUIREMENTS,
    )
    assert not result["eligible"]
    assert result["eligibility"]["mandatory_requirements_missing"] == ["Node.js"]
