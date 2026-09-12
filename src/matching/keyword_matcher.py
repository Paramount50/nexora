"""Deterministic requirement-level lexical matching."""

from __future__ import annotations

import re
from typing import Any

from rapidfuzz.fuzz import ratio

from src.matching.normalization import ALIASES, extract_skill_mentions, normalize_skill


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


EVIDENCE_SOURCE_REASON_CODES = {
    "projects_section": "PROJECT_EVIDENCE",
    "project": "PROJECT_EVIDENCE",
    "work_history": "WORK_EXPERIENCE_EVIDENCE",
    "experience": "WORK_EXPERIENCE_EVIDENCE",
    "education_section": "EDUCATION_EVIDENCE",
    "education": "EDUCATION_EVIDENCE",
    "certification_section": "CERTIFICATION_EVIDENCE",
    "certifications": "CERTIFICATION_EVIDENCE",
    "skills_section": "SKILLS_SECTION_EVIDENCE",
    "skills": "SKILLS_SECTION_EVIDENCE",
}


def match_requirement(requirement: dict[str, Any], evidence_items: list[dict[str, Any]]) -> dict[str, Any]:
    canonical_name = requirement["canonical_name"]
    canonical_skill = normalize_skill(canonical_name) or canonical_name
    acceptable_skills = {
        normalize_skill(skill) or skill for skill in requirement.get("acceptable_skills", [])
    }
    acceptable_skills.add(canonical_skill)
    text_patterns = requirement.get("text_patterns", [])
    related_skills = {
        normalize_skill(skill) or skill for skill in requirement.get("related_skills", [])
    }
    best_match: dict[str, Any] | None = None
    previous_text = ""
    previous_section = ""

    for evidence in evidence_items:
        section = evidence.get("section", "")
        context_evidence = evidence
        if section and section == previous_section:
            context_evidence = {**evidence, "text": f"{previous_text} {evidence.get('text', '')}"}
        match_type = classify_match(canonical_skill, related_skills, context_evidence, acceptable_skills, text_patterns)
        previous_text = evidence.get("text", "")
        previous_section = section
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
    reason_codes = list({
        "exact": ["EXACT_KEYWORD"],
        "alias": ["ALIAS_MATCH"],
        "fuzzy": ["FUZZY_MATCH"],
        "related": ["RELATED_SKILL"],
    }[match_type])
    source_key = evidence.get("evidence_source_type") or evidence.get("section")
    if source_key in EVIDENCE_SOURCE_REASON_CODES:
        reason_codes.append(EVIDENCE_SOURCE_REASON_CODES[source_key])
    if evidence.get("evidence_strength") == "substantial":
        reason_codes.append("SUBSTANTIAL_EVIDENCE")
    return build_result(
        requirement,
        match_type,
        evidence,
        MATCH_SCORES[match_type],
        best_match["evidence_strength_score"],
        reason_codes,
    )


def classify_match(
    canonical_skill: str,
    related_skills: set[str],
    evidence: dict[str, Any],
    acceptable_skills: set[str] | None = None,
    text_patterns: list[str] | None = None,
) -> str:
    text = evidence.get("text", "")
    mentions = extract_skill_mentions(text)
    acceptable_skills = acceptable_skills or {canonical_skill}
    if any(re.search(pattern, text, re.IGNORECASE) for pattern in (text_patterns or [])):
        return "exact"
    direct_matches = [
        skill for skill in acceptable_skills
        if skill in mentions and not explicitly_negated(text, skill)
    ]
    if direct_matches:
        return "exact" if any(contains_literal_skill(text, skill) for skill in direct_matches) else "alias"
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


def explicitly_negated(text: str, canonical_skill: str) -> bool:
    """Avoid treating a resume's stated absence of a skill as evidence."""
    names = [canonical_skill]
    names.extend(alias for alias, canonical in ALIASES.items() if canonical == canonical_skill)
    negation = r"(?:no|not|without|never|has not|have not|hasn't|haven't)"
    return any(
        re.search(rf"{negation}[^.\n]{{0,80}}(?<!\w){re.escape(name)}(?!\w)", text, re.IGNORECASE)
        for name in names
    )


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
        "evidence_id": evidence.get("evidence_id") if evidence else None,
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
