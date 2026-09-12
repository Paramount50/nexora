"""Unified lexical engine for deterministic matching and BM25 retrieval."""

from __future__ import annotations

from typing import Any

from src.matching.bm25_retriever import BM25Retriever
from src.matching.keyword_matcher import match_requirement


class KeywordEngine:
    def __init__(self, evidence_items: list[dict[str, Any]]) -> None:
        self.evidence_items = evidence_items
        self.retriever = BM25Retriever(evidence_items) if evidence_items else None

    def match_candidate(
        self,
        requirement: dict[str, Any],
        candidate_evidence: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return match_requirement(requirement, candidate_evidence)

    def retrieve(
        self,
        requirement: dict[str, Any],
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        if self.retriever is None:
            return []
        query = " ".join(
            part
            for part in (
                requirement.get("canonical_name", ""),
                requirement.get("source_text", ""),
                " ".join(requirement.get("aliases", [])),
                " ".join(requirement.get("related_skills", [])),
            )
            if part
        )
        return self.retriever.retrieve(query, top_k=top_k)
