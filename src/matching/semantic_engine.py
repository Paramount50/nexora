"""Semantic similarity over JD requirements and resume evidence."""

from __future__ import annotations

import hashlib
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
        self._evidence_cache_key: str | None = None
        self._evidence_vectors: np.ndarray | None = None
        self._query_cache: dict[str, np.ndarray] = {}

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

        evidence_vectors = self._get_evidence_vectors(evidence_items, evidence_texts)
        query_vector = self._get_query_vector(query)
        similarities = cosine_similarity(query_vector.reshape(1, -1), evidence_vectors)[0]
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

    def _get_evidence_vectors(
        self, evidence_items: list[dict[str, Any]], evidence_texts: list[str]
    ) -> np.ndarray:
        cache_key = hash_texts(evidence_texts)
        if cache_key != self._evidence_cache_key or self._evidence_vectors is None:
            self._evidence_vectors = self.embedder.encode(evidence_texts)
            self._evidence_cache_key = cache_key
            self._query_cache.clear()
        return self._evidence_vectors

    def _get_query_vector(self, query: str) -> np.ndarray:
        cache_key = hashlib.sha256(query.encode("utf-8")).hexdigest()
        if cache_key not in self._query_cache:
            self._query_cache[cache_key] = self.embedder.encode([query])[0]
        return self._query_cache[cache_key]


def requirement_text(requirement: dict[str, Any]) -> str:
    values = [
        requirement.get("canonical_name", ""),
        requirement.get("source_text", ""),
        " ".join(requirement.get("aliases", [])),
        " ".join(requirement.get("related_skills", [])),
    ]
    return " ".join(value for value in values if value)


def hash_texts(texts: list[str]) -> str:
    digest = hashlib.sha256()
    for text in texts:
        digest.update(text.encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()
