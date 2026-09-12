"""Comprehensive unit and integration tests for matching, evidence classification, and fusion."""

from pathlib import Path
from src.matching.keyword_matcher import match_requirement, classify_match, is_controlled_fuzzy_match
from src.matching.normalization import extract_skill_mentions, normalize_skill
from src.matching.score_fusion import fuse_requirement_result
from src.matching.ranker import rank_candidates, rank_candidate
from src.parsing.resume_loader import classify_evidence, build_candidate
from src.parsing.section_detector import detect_sections, normalize_heading
from src.parsing.jd_loader import extract_requirements, infer_importance
from src.pipeline import rank_documents


def test_evidence_classification_and_strength() -> None:
    # Skills section -> mentioned
    ev_type, ev_source, ev_strength = classify_evidence("skills", "Python, React, Docker")
    assert ev_type == "skill_list"
    assert ev_source == "skills_section"
    assert ev_strength == "mentioned"

    # Work experience with impact words -> substantial
    ev_type, ev_source, ev_strength = classify_evidence(
        "experience",
        "Developed and architected high-throughput microservices handling 50k requests per second using Node.js and Redis",
    )
    assert ev_type == "work_experience"
    assert ev_source == "work_history"
    assert ev_strength == "substantial"

    # Projects section
    ev_type, ev_source, ev_strength = classify_evidence(
        "projects",
        "Built a real-time collaborative code editor with WebSockets and React",
    )
    assert ev_type == "project_or_experience"
    assert ev_source == "projects_section"
    assert ev_strength == "substantial"


def test_reason_codes_correctness() -> None:
    req = {
        "requirement_id": "req_01",
        "canonical_name": "Node.js",
        "importance": "required",
        "related_skills": ["Express.js"],
    }
    # Test work history evidence gets WORK_EXPERIENCE_EVIDENCE
    evidence_work = [
        {
            "candidate_id": "cand_01",
            "evidence_id": "e_01",
            "section": "experience",
            "evidence_source_type": "work_history",
            "evidence_strength": "substantial",
            "text": "Engineered backend microservices in Node.js",
        }
    ]
    result_work = match_requirement(req, evidence_work)
    assert "EXACT_KEYWORD" in result_work["reason_codes"]
    assert "WORK_EXPERIENCE_EVIDENCE" in result_work["reason_codes"]
    assert "SUBSTANTIAL_EVIDENCE" in result_work["reason_codes"]
    assert "PROJECT_EVIDENCE" not in result_work["reason_codes"]

    # Test project evidence gets PROJECT_EVIDENCE
    evidence_proj = [
        {
            "candidate_id": "cand_02",
            "evidence_id": "e_02",
            "section": "projects",
            "evidence_source_type": "projects_section",
            "evidence_strength": "applied",
            "text": "Built a pet project using Node.js",
        }
    ]
    result_proj = match_requirement(req, evidence_proj)
    assert "PROJECT_EVIDENCE" in result_proj["reason_codes"]
    assert "WORK_EXPERIENCE_EVIDENCE" not in result_proj["reason_codes"]


def test_adversarial_skill_confusions() -> None:
    # Java must NOT match JavaScript
    assert not is_controlled_fuzzy_match("Java", "JavaScript")
    assert not is_controlled_fuzzy_match("JavaScript", "Java")

    # React must NOT match React Native as exact
    mentions = extract_skill_mentions("Experienced in React Native mobile app development")
    assert "React Native" in mentions
    # React Native mention shouldn't falsely normalize to plain React
    assert normalize_skill("react native") == "React Native"


def test_bm25_and_semantic_score_fusion() -> None:
    keyword_res = {
        "requirement_id": "req_01",
        "canonical_name": "FastAPI",
        "importance": "required",
        "match_type": "none",
        "keyword_score": 0.0,
        "evidence_strength_score": 0.0,
        "missing": True,
    }
    semantic_res = {
        "candidate_id": "cand_01",
        "evidence_id": "ev_05",
        "semantic_score": 0.85,
        "evidence_text": "Built Python REST API microservices with asynchronous endpoints",
    }
    bm25_res = {
        "candidate_id": "cand_01",
        "evidence_id": "ev_05",
        "normalized_score": 0.70,
        "evidence_text": "Built Python REST API microservices",
    }

    fused = fuse_requirement_result(keyword_res, semantic_res, bm25_result=bm25_res)
    assert fused["fused_score"] > 0.4
    assert fused["bm25_score"] == 0.70
    assert fused["semantic_score"] == 0.85
    assert fused["semantic_match"] is True
    assert fused["bm25_match"] is True
    assert fused["semantic_evidence_id"] == "ev_05"
    assert fused["bm25_evidence_id"] == "ev_05"


def test_section_detector_noisy_headings() -> None:
    text = """
    ### 1. TECHNICAL SKILLS:
    Python, SQL, Docker

    EXPERIENCE | Professional Work History:
    Senior Developer at ACME Corp
    Built scalable data pipelines

    * Projects & Open Source *
    Nexora Ranking Engine
    """
    sections = detect_sections(text)
    assert "skills" in sections
    assert "Python, SQL, Docker" in sections["skills"]
    assert "experience" in sections
    assert "projects" in sections


def test_jd_requirement_extraction_importance() -> None:
    jd_text = """
    Senior Full Stack Engineer
    
    Requirements:
    - Must have 3+ years experience with Python and FastAPI
    - Strong proficiency in PostgreSQL is mandatory
    
    Preferred Qualifications:
    - Experience with Docker is a plus
    - Nice to have: GraphQL and Tailwind CSS
    """
    extracted = extract_requirements(jd_text)
    reqs = {r["canonical_name"]: r for r in extracted["requirements"]}
    
    assert "Python" in reqs
    assert reqs["Python"]["importance"] == "required"
    assert "PostgreSQL" in reqs
    assert reqs["PostgreSQL"]["importance"] == "required"
    assert "Docker" in reqs
    assert reqs["Docker"]["importance"] == "nice_to_have"
    assert "GraphQL" in reqs
    assert reqs["GraphQL"]["importance"] == "nice_to_have"
