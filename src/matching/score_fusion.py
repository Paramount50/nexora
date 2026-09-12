"""Fuse lexical, semantic, and evidence-strength signals per requirement."""

from __future__ import annotations

from typing import Any


DEFAULT_CONFIG = {
    "keyword_weight": 0.40,
    "semantic_weight": 0.35,
    "bm25_weight": 0.15,
    "evidence_strength_weight": 0.10,
}


def fuse_requirement_result(
    keyword_result: dict[str, Any],
    semantic_result: dict[str, Any] | None = None,
    bm25_result: dict[str, Any] | None = None,
    config: dict[str, float] | None = None,
) -> dict[str, Any]:
    settings = {**DEFAULT_CONFIG, **(config or {})}
    keyword_score = clamp(keyword_result.get("keyword_score", 0.0))
    semantic_score = clamp((semantic_result or {}).get("semantic_score", 0.0))
    bm25_score = clamp((bm25_result or {}).get("normalized_score", 0.0))

    # Evidence strength: reconcile keyword evidence strength and semantic/bm25 evidence
    evidence_strength = clamp(keyword_result.get("evidence_strength_score", 0.0))
    if evidence_strength == 0.0 and semantic_result and semantic_score >= 0.6:
        evidence_strength = 0.5

    semantic_evidence = semantic_result.get("evidence_text", "") if semantic_result else ""
    bm25_evidence = bm25_result.get("evidence_text", "") if bm25_result else ""

    weights = {
        "keyword": settings.get("keyword_weight", DEFAULT_CONFIG["keyword_weight"]),
        "semantic": settings.get("semantic_weight", DEFAULT_CONFIG["semantic_weight"]),
        "bm25": settings.get("bm25_weight", DEFAULT_CONFIG["bm25_weight"]),
        "evidence_strength": settings.get("evidence_strength_weight", DEFAULT_CONFIG["evidence_strength_weight"]),
    }
    total_weight = sum(weights.values())
    fused_score = (
        weights["keyword"] * keyword_score
        + weights["semantic"] * semantic_score
        + weights["bm25"] * bm25_score
        + weights["evidence_strength"] * evidence_strength
    ) / total_weight if total_weight else 0.0

    result = {
        **keyword_result,
        "bm25_score": bm25_score,
        "semantic_score": semantic_score,
        "fused_score": clamp(fused_score),
        "semantic_match": semantic_result is not None and semantic_score > 0.0,
        "bm25_match": bm25_result is not None and bm25_score > 0.0,
        "semantic_evidence_text": [semantic_evidence] if semantic_evidence else [],
    }
    if semantic_result and semantic_result.get("evidence_id"):
        result["semantic_evidence_id"] = semantic_result["evidence_id"]
    if bm25_result and bm25_result.get("evidence_id"):
        result["bm25_evidence_id"] = bm25_result["evidence_id"]
    return result


def clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))
