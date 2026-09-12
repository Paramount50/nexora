"""Deterministic requirement-level lexical matching."""

from __future__ import annotations

import re
from typing import Any

from rapidfuzz.fuzz import ratio

from src.matching.normalization import extract_skill_mentions, normalize_skill


EVIDENCE_STRENGTH_SCORES = {
    "substantial": 1.0,
    "applied": 0.65,
    "mentioned": 0.35,
}

MATCH_SCORES = {
    "exact": 1.0,
    "alias": 0.9,
    "fuzzy": 0.75,
    "related": 0.5,
    "none": 0.0,
}


def match_requirement(requirement: dict[str, Any], evidence_items: list[dict[str, Any]]) -> dict[str, Any]:
    canonical_name = requirement["canonical_name"]
    canonical_skill = normalize_skill(canonical_name) or canonical_name
    related_skills = {
        normalize_skill(skill) or skill for skill in requirement.get("related_skills", [])
    }
    best_match: dict[str, Any] | None = None

    for evidence in evidence_items:
        match_type = classify_match(canonical_skill, related_skills, evidence)
        if match_type == "none":
            continue
        score = MATCH_SCORES[match_type]
        strength_score = EVIDENCE_STRENGTH_SCORES.get(evidence.get("evidence_strength"), 0.0)
        candidate = (score, strength_score, evidence)
        if best_match is None or candidate[:2] > best_match["sort_key"]:
            best_match = {
                "sort_key": candidate[:2],
                "match_type": match_type,
                "evidence": evidence,
                "evidence_strength_score": strength_score,
            }

    if best_match is None:
        return build_result(requirement, "none", None, 0.0, 0.0)

    match_type = best_match["match_type"]
    evidence = best_match["evidence"]
    reason_codes = {
        "exact": ["EXACT_KEYWORD"],
        "alias": ["ALIAS_MATCH"],
        "fuzzy": ["FUZZY_MATCH"],
        "related": ["RELATED_SKILL"],
    }[match_type]
    if evidence.get("evidence_source_type") in {"project", "experience"}:
        reason_codes.append("PROJECT_EVIDENCE")
    return build_result(
        requirement,
        match_type,
        evidence,
        MATCH_SCORES[match_type],
        best_match["evidence_strength_score"],
        reason_codes,
    )


def classify_match(canonical_skill: str, related_skills: set[str], evidence: dict[str, Any]) -> str:
    text = evidence.get("text", "")
    mentions = extract_skill_mentions(text)
    if canonical_skill in mentions:
        return "exact" if contains_literal_skill(text, canonical_skill) else "alias"
    if any(mention in related_skills for mention in mentions):
        return "related"
    fuzzy_terms = mentions + re.findall(r"[a-zA-Z][a-zA-Z0-9.+#-]{2,}", text)
    if any(is_controlled_fuzzy_match(canonical_skill, term) for term in fuzzy_terms):
        return "fuzzy"
    return "none"


def is_controlled_fuzzy_match(canonical_skill: str, mention: str, threshold: int = 92) -> bool:
    if canonical_skill.lower() == mention.lower():
        return False
    if abs(len(canonical_skill) - len(mention)) > 2:
        return False
    return ratio(canonical_skill.lower(), mention.lower()) >= threshold


def contains_literal_skill(text: str, canonical_skill: str) -> bool:
    pattern = re.escape(canonical_skill)
    return re.search(rf"(?<!\w){pattern}(?!\w)", text, flags=re.IGNORECASE) is not None


def build_result(
    requirement: dict[str, Any],
    match_type: str,
    evidence: dict[str, Any] | None,
    keyword_score: float,
    evidence_strength_score: float,
    reason_codes: list[str] | None = None,
) -> dict[str, Any]:
    matched = evidence is not None
    return {
        "candidate_id": evidence.get("candidate_id") if evidence else None,
        "requirement_id": requirement["requirement_id"],
        "canonical_name": requirement["canonical_name"],
        "importance": requirement["importance"],
        "match_type": match_type,
        "keyword_score": keyword_score,
        "semantic_score": 0.0,
        "evidence_strength_score": evidence_strength_score,
        "confidence": keyword_score * evidence_strength_score,
        "status": "strong_match" if match_type == "exact" else "moderate_match" if matched else "no_evidence",
        "exact_match": match_type == "exact",
        "alias_match": match_type == "alias",
        "fuzzy_match": match_type == "fuzzy",
        "semantic_match": False,
        "reason_codes": reason_codes or [],
        "evidence_text": [evidence["text"]] if evidence else [],
        "missing": not matched,
        "notes": "" if matched else "No lexical evidence found for this requirement.",
    }
