"""Generate structured, evidence-grounded ranking explanations."""

from __future__ import annotations

from typing import Any


def explain_top_candidates(
    rankings: list[dict[str, Any]],
    limit: int = 3,
) -> list[dict[str, Any]]:
    return [build_explanation(item) for item in rankings[:limit]]


def build_explanation(ranking: dict[str, Any]) -> dict[str, Any]:
    results = ranking.get("requirement_results", [])
    strongest = sorted(
        (result for result in results if not result.get("missing")),
        key=lambda result: result.get("fused_score", 0.0),
        reverse=True,
    )
    strongest_matches = [
        f"{result['canonical_name']}: {result['evidence_text'][0]}"
        for result in strongest[:3]
        if result.get("evidence_text")
    ]
    missing_or_weak = [
        result["canonical_name"]
        for result in results
        if result.get("missing") or result.get("fused_score", 0.0) < 0.5
    ]
    evidence_refs = []
    reason_codes = []
    for result in strongest[:3]:
        for key in ("evidence_id", "semantic_evidence_id"):
            evidence_id = result.get(key)
            if evidence_id and evidence_id not in evidence_refs:
                evidence_refs.append(evidence_id)
        for code in result.get("reason_codes", []):
            if code not in reason_codes:
                reason_codes.append(code)
        if result.get("semantic_match") and "SEMANTIC_MATCH" not in reason_codes:
            reason_codes.append("SEMANTIC_MATCH")

    return {
        "candidate_id": ranking["candidate_id"],
        "rank": ranking.get("rank"),
        "summary": build_summary(ranking, strongest, missing_or_weak),
        "strongest_matches": strongest_matches,
        "missing_or_weak": missing_or_weak,
        "evidence_refs": evidence_refs,
        "reason_codes": reason_codes,
    }


def build_summary(
    ranking: dict[str, Any],
    strongest: list[dict[str, Any]],
    missing_or_weak: list[str],
) -> str:
    match_count = len(strongest)
    if missing_or_weak:
        return (
            f"{ranking.get('candidate_name', 'Candidate')} has {match_count} supported requirement matches, "
            f"with gaps or weak evidence for {', '.join(missing_or_weak[:3])}."
        )
    return f"{ranking.get('candidate_name', 'Candidate')} has {match_count} supported requirement matches with no recorded gaps."