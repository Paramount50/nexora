"""Semantic similarity over JD requirements and resume evidence."""

from __future__ import annotations

from typing import Any, Protocol

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class Embedder(Protocol):
    def encode(self, texts: list[str]) -> np.ndarray:
        """Return one embedding vector per input text."""


class SentenceTransformerEmbedder:
    """Adapter for a locally available sentence-transformers model."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as error:
            raise RuntimeError(
                "Semantic matching requires sentence-transformers. "
                "Install it before constructing SentenceTransformerEmbedder."
            ) from error
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: list[str]) -> np.ndarray:
        return np.asarray(self.model.encode(texts, normalize_embeddings=True))


class SemanticEngine:
    def __init__(self, embedder: Embedder) -> None:
        self.embedder = embedder

    def match_requirement(
        self,
        requirement: dict[str, Any],
        evidence_items: list[dict[str, Any]],
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        query = requirement_text(requirement)
        evidence_texts = [item.get("text", "") for item in evidence_items]
        if not evidence_texts:
            return []

        vectors = self.embedder.encode([query, *evidence_texts])
        similarities = cosine_similarity(vectors[0:1], vectors[1:])[0]
        indexes = sorted(range(len(similarities)), key=lambda index: similarities[index], reverse=True)[:top_k]
        return [
            {
                "candidate_id": evidence_items[index].get("candidate_id"),
                "evidence_id": evidence_items[index].get("evidence_id"),
                "evidence_text": evidence_items[index].get("text", ""),
                "semantic_score": float(similarities[index]),
            }
            for index in indexes
        ]


def requirement_text(requirement: dict[str, Any]) -> str:
    values = [
        requirement.get("canonical_name", ""),
        requirement.get("source_text", ""),
        " ".join(requirement.get("aliases", [])),
        " ".join(requirement.get("related_skills", [])),
    ]
    return " ".join(value for value in values if value)
