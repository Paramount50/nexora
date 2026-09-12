"""BM25 retrieval over structured resume evidence chunks."""

from __future__ import annotations

import re
from typing import Any

from rank_bm25 import BM25Okapi


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9+#.]+", text.lower())


class BM25Retriever:
    def __init__(self, evidence_items: list[dict[str, Any]]) -> None:
        self.evidence_items = evidence_items
        self._tokenized_documents = [tokenize(item.get("text", "")) for item in evidence_items]
        self._index = BM25Okapi(self._tokenized_documents)

    def retrieve(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        scores = self._index.get_scores(tokenize(query))
        ranked_indexes = sorted(range(len(scores)), key=lambda index: scores[index], reverse=True)
        selected = ranked_indexes[:top_k]
        max_score = max((scores[index] for index in selected), default=0.0)

        results = []
        for index in selected:
            item = self.evidence_items[index]
            raw_score = float(scores[index])
            results.append(
                {
                    "candidate_id": item.get("candidate_id"),
                    "evidence_id": item.get("evidence_id"),
                    "evidence_text": item.get("text", ""),
                    "raw_score": raw_score,
                    "normalized_score": raw_score / max_score if max_score > 0 else 0.0,
                }
            )
        return results


def retrieve_requirement(
    requirement: dict[str, Any], evidence_items: list[dict[str, Any]], top_k: int = 5
) -> list[dict[str, Any]]:
    query_parts = [
        requirement.get("canonical_name", ""),
        requirement.get("source_text", ""),
        " ".join(requirement.get("aliases", [])),
        " ".join(requirement.get("related_skills", [])),
    ]
    query = " ".join(part for part in query_parts if part)
    return BM25Retriever(evidence_items).retrieve(query, top_k=top_k)