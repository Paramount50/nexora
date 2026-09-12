import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.parsing.jd_loader import extract_jd_text, extract_requirements
from src.parsing.resume_loader import load_resume_directory
from src.matching.semantic_engine import SentenceTransformerEmbedder, SemanticEngine
from src.pipeline import rank_documents
from src.explanations.explanation import explain_top_candidates


def main():
    jd_path = ROOT / "data" / "runtime" / "Sample_JD.pdf"
    resumes_dir = ROOT / "data" / "runtime" / "Testing Dataset"

    print("Extracting JD...")
    jd_text = extract_jd_text(jd_path)
    jd_data = extract_requirements(jd_text)
    reqs = jd_data["requirements"]
    print(f"Role: {jd_data['job_title']}")
    print(f"Extracted {len(reqs)} requirements.")

    print("\nLoading 18 Resumes...")
    candidates = load_resume_directory(resumes_dir, ("pdf",))
    print(f"Loaded {len(candidates)} resumes.")

    print("\nInitializing Semantic Engine...")
    embedder = SentenceTransformerEmbedder("all-MiniLM-L6-v2")
    engine = SemanticEngine(embedder)

    print("\nRunning Hybrid Ranking...")
    rankings = rank_documents(candidates, reqs, semantic_engine=engine)

    print("\n=== TOP RANKINGS ===")
    for r in rankings:
        print(f"Rank {r['rank']:2d}: {r['candidate_name']:<20} | Score: {r['final_score']:5.2f} | Eligible: {str(r['eligible']):<5} | Mandatory Cov: {r['mandatory_coverage']:.2%} | Missing: {r['missing_requirements']}")

    print("\n=== TOP 3 EXPLANATIONS ===")
    explanations = explain_top_candidates(rankings)
    for exp in explanations[:3]:
        print(f"\n--- {exp['candidate_name']} (Rank {exp['rank']}) ---")
        print("Strongest Matches:", exp["strongest_matches"])
        print("Missing / Weak:", exp["missing_or_weak"])
        print("Reason Codes:", exp["reason_codes"])
        print("Summary:", exp["summary"])


if __name__ == "__main__":
    main()
