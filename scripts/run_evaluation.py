import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data_loader import load_dataset
from src.evaluation.metrics import evaluate_ranking
from src.evaluation.ranking_comparison import compare_rankings
from src.evaluation.failure_analysis import find_failures
from src.matching.semantic_engine import SentenceTransformerEmbedder, SemanticEngine
from src.pipeline import rank_documents


def main():
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    dataset, requirement_data = load_dataset(data_dir)
    labels = json.loads((data_dir / "mock_labels.json").read_text(encoding="utf-8"))["labels"]

    print(f"Loaded {len(dataset['candidates'])} candidates and {len(requirement_data['requirements'])} requirements.")

    # 1. Keyword only
    print("\n--- 1. Keyword-Only Mode ---")
    keyword_config = {"keyword_weight": 0.65, "semantic_weight": 0.0, "bm25_weight": 0.25, "evidence_strength_weight": 0.10}
    kw_rankings = rank_documents(dataset["candidates"], requirement_data["requirements"], fusion_config=keyword_config)
    kw_metrics = evaluate_ranking(kw_rankings, labels, top_k=10)
    print(f"Pairwise agreement: {kw_metrics['pairwise_agreement']:.3%}")
    print(f"Top 10 band distribution: {kw_metrics['top_k_band_counts']}")

    # 2. Semantic only
    print("\n--- 2. Semantic-Only Mode ---")
    embedder = SentenceTransformerEmbedder("all-MiniLM-L6-v2")
    engine = SemanticEngine(embedder)
    sem_config = {"keyword_weight": 0.0, "semantic_weight": 0.85, "bm25_weight": 0.0, "evidence_strength_weight": 0.15}
    sem_rankings = rank_documents(dataset["candidates"], requirement_data["requirements"], semantic_engine=engine, fusion_config=sem_config)
    sem_metrics = evaluate_ranking(sem_rankings, labels, top_k=10)
    print(f"Pairwise agreement: {sem_metrics['pairwise_agreement']:.3%}")
    print(f"Top 10 band distribution: {sem_metrics['top_k_band_counts']}")

    # 3. Hybrid mode
    print("\n--- 3. Hybrid Mode (BM25 + Semantic + Lexical + Evidence Strength) ---")
    hybrid_config = {"keyword_weight": 0.40, "semantic_weight": 0.35, "bm25_weight": 0.15, "evidence_strength_weight": 0.10}
    hybrid_rankings = rank_documents(dataset["candidates"], requirement_data["requirements"], semantic_engine=engine, fusion_config=hybrid_config)
    hybrid_metrics = evaluate_ranking(hybrid_rankings, labels, top_k=10)
    print(f"Pairwise agreement: {hybrid_metrics['pairwise_agreement']:.3%}")
    print(f"Top 10 band distribution: {hybrid_metrics['top_k_band_counts']}")

    # Comparison summary
    comparison = compare_rankings(kw_rankings, sem_rankings, hybrid_rankings, top_k=5)
    print("\n--- Summary Comparison ---")
    for mode, data in comparison.items():
        print(f"[{mode.upper()}] Eligible: {data['eligible_count']}, Score Range: {data['score_min']:.1f} - {data['score_max']:.1f}")

    failures = find_failures(hybrid_rankings, labels, limit=5)
    print(f"\nHybrid Ranking Inversions / Violations: {len(failures)}")


if __name__ == "__main__":
    main()
