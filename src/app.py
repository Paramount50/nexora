"""Streamlit demo for the evidence-first ranking pipeline."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st

from src.explanations.explanation import explain_top_candidates
from src.explanations.recruiter_chat import answer_why_ranked_above
from src.matching.semantic_engine import SentenceTransformerEmbedder, SemanticEngine
from src.pipeline import rank_documents, rank_uploaded_inputs, run_pipeline

DATA_DIR = ROOT / "data"


@st.cache_data(show_spinner=False)
def load_keyword_ranking() -> list[dict]:
    return run_pipeline(DATA_DIR)


@st.cache_resource(show_spinner="Loading embedding model...")
def load_semantic_engine() -> SemanticEngine:
    return SemanticEngine(SentenceTransformerEmbedder("all-MiniLM-L6-v2"))


def selected_pipeline(mode: str):
    if mode == "Keyword only":
        return None, {"keyword_weight": 0.65, "semantic_weight": 0.0, "bm25_weight": 0.25, "evidence_strength_weight": 0.10}
    engine = load_semantic_engine()
    if mode == "Semantic only":
        return engine, {"keyword_weight": 0.0, "semantic_weight": 0.85, "bm25_weight": 0.0, "evidence_strength_weight": 0.15}
    return engine, {"keyword_weight": 0.40, "semantic_weight": 0.35, "bm25_weight": 0.15, "evidence_strength_weight": 0.10}


def main() -> None:
    st.set_page_config(page_title="Nexora Resume Ranking", layout="wide")
    st.title("Nexora Resume Ranking")
    st.caption("Evidence-first candidate ranking engine with lexical, BM25, and semantic score fusion")

    mode = st.radio("Ranking mode", ["Keyword only", "Semantic only", "Hybrid"], horizontal=True)
    semantic_engine, fusion_config = selected_pipeline(mode)
    jd_upload = st.file_uploader("Job description (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
    resume_uploads = st.file_uploader(
        "Resume files (PDF, DOCX, TXT, XML)", type=["pdf", "docx", "txt", "xml"], accept_multiple_files=True
    )
    if jd_upload and resume_uploads:
        rankings, bias_findings = rank_uploaded_inputs(jd_upload, resume_uploads, semantic_engine, fusion_config)
        st.success(f"Ranked {len(rankings)} uploaded candidates against {jd_upload.name}")
    else:
        rankings = run_pipeline(DATA_DIR, semantic_engine=semantic_engine, fusion_config=fusion_config, prefer_runtime=True)
        bias_findings = []
        st.info("Loaded runtime evaluation dataset: **Sample_JD.pdf** + **18 candidate resumes**. Upload files above to test on custom inputs.")

    if bias_findings:
        with st.expander("Potential JD phrasing concerns"):
            st.warning("Review these flags with a human recruiter; they are prompts for review, not automatic rejection.")
            st.dataframe(pd.DataFrame(bias_findings), use_container_width=True, hide_index=True)

    explanations = explain_top_candidates(rankings)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Candidates", len(rankings))
    col2.metric("Eligible Candidates", sum(item["eligible"] for item in rankings))
    col3.metric("Ranking Mode", mode)

    table = pd.DataFrame(
        [
            {
                "Rank": item["rank"],
                "Candidate": item["candidate_name"],
                "Final score": item["final_score"],
                "Eligible": "Yes" if item["eligible"] else "No",
                "Mandatory coverage": f"{item['mandatory_coverage']:.1%}",
                "Preferred coverage": f"{item['preferred_coverage']:.1%}",
                "Missing requirements": ", ".join(item["missing_requirements"]),
            }
            for item in rankings
        ]
    )
    st.dataframe(table, use_container_width=True, hide_index=True)

    st.subheader("Candidate detail")
    candidate_names = {item["candidate_name"]: item for item in rankings}
    selected_name = st.selectbox("Select candidate", list(candidate_names))
    selected = candidate_names[selected_name]
    st.write(selected["eligibility"])
    st.write(selected["fit"])
    for result in selected["requirement_results"]:
        with st.expander(f"{result['canonical_name']} ({result['importance'].upper()}) - Fused Score: {result['fused_score']:.2f}"):
            st.write({
                "match_type": result["match_type"],
                "keyword_score": result["keyword_score"],
                "bm25_score": result.get("bm25_score", 0.0),
                "semantic_score": result["semantic_score"],
                "fused_score": result["fused_score"],
                "missing": result["missing"],
                "reason_codes": result["reason_codes"],
                "evidence": result["evidence_text"],
            })

    st.subheader("Candidate comparison")
    comparison_names = st.multiselect(
        "Choose two candidates",
        list(candidate_names),
        default=list(candidate_names)[:2],
        max_selections=2,
    )
    if len(comparison_names) == 2:
        left, right = (candidate_names[name] for name in comparison_names)
        comparison_rows = []
        for left_result, right_result in zip(left["requirement_results"], right["requirement_results"]):
            comparison_rows.append(
                {
                    "Requirement": left_result["canonical_name"],
                    f"{left['candidate_name']} score": round(left_result["fused_score"], 3),
                    f"{right['candidate_name']} score": round(right_result["fused_score"], 3),
                    f"{left['candidate_name']} match": left_result["match_type"],
                    f"{right['candidate_name']} match": right_result["match_type"],
                }
            )
        st.dataframe(pd.DataFrame(comparison_rows), use_container_width=True, hide_index=True)
        higher, lower = sorted((left, right), key=lambda item: item["rank"])
        st.write(answer_why_ranked_above(higher, lower))

    st.subheader("Top 3 explanations")
    for explanation in explanations:
        st.markdown(f"**#{explanation['rank']} {explanation.get('candidate_name', explanation['candidate_id'])}**")
        st.write(explanation["summary"])
        st.write({
            "strongest_matches": explanation["strongest_matches"],
            "missing_or_weak": explanation["missing_or_weak"],
            "evidence_refs": explanation["evidence_refs"],
            "reason_codes": explanation["reason_codes"],
        })


if __name__ == "__main__":
    main()