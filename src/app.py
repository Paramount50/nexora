"""Streamlit demo for the evidence-first ranking pipeline."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.explanations.explanation import explain_top_candidates
from src.parsing.jd_loader import extract_requirements
from src.parsing.resume_loader import load_resume
from src.matching.semantic_engine import SentenceTransformerEmbedder, SemanticEngine
from src.pipeline import rank_documents, run_pipeline


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


@st.cache_data(show_spinner=False)
def load_keyword_ranking() -> list[dict]:
    return run_pipeline(DATA_DIR)


@st.cache_resource(show_spinner="Loading embedding model...")
def load_semantic_engine() -> SemanticEngine:
    return SemanticEngine(SentenceTransformerEmbedder("all-MiniLM-L6-v2"))


def selected_pipeline(mode: str):
    if mode == "Keyword only":
        return None, {"keyword_weight": 1.0, "semantic_weight": 0.0, "evidence_strength_weight": 0.0}
    engine = load_semantic_engine()
    if mode == "Semantic only":
        return engine, {"keyword_weight": 0.0, "semantic_weight": 1.0, "evidence_strength_weight": 0.0}
    return engine, {"keyword_weight": 0.5, "semantic_weight": 0.5, "evidence_strength_weight": 0.15}


def rank_uploaded_inputs(jd_upload, resume_uploads, semantic_engine=None, fusion_config=None):
    import tempfile

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        jd_path = root / jd_upload.name
        jd_path.write_bytes(jd_upload.getvalue())
        requirements = extract_requirements(jd_path)["requirements"]
        candidates = []
        for upload in resume_uploads:
            path = root / upload.name
            path.write_bytes(upload.getvalue())
            candidates.append(load_resume(path))
        return rank_documents(
            candidates,
            requirements,
            semantic_engine=semantic_engine,
            fusion_config=fusion_config,
        )


def main() -> None:
    st.set_page_config(page_title="Nexora Resume Ranking", layout="wide")
    st.title("Nexora Resume Ranking")
    st.caption("Evidence-first candidate ranking over the synthetic development dataset")

    mode = st.radio("Ranking mode", ["Keyword only", "Semantic only", "Hybrid"], horizontal=True)
    semantic_engine, fusion_config = selected_pipeline(mode)
    jd_upload = st.file_uploader("Job description", type=["pdf", "docx", "txt"])
    resume_uploads = st.file_uploader(
        "Resume files", type=["pdf", "docx", "txt", "xml"], accept_multiple_files=True
    )
    if jd_upload and resume_uploads:
        rankings = rank_uploaded_inputs(jd_upload, resume_uploads, semantic_engine, fusion_config)
    else:
        rankings = run_pipeline(DATA_DIR, semantic_engine=semantic_engine, fusion_config=fusion_config)
        st.info("Showing the synthetic development dataset. Upload a JD and resumes to rank runtime inputs.")
    explanations = explain_top_candidates(rankings)
    st.metric("Candidates", len(rankings))
    st.metric("Eligible candidates", sum(item["eligible"] for item in rankings))

    table = pd.DataFrame(
        [
            {
                "Rank": item["rank"],
                "Candidate": item["candidate_name"],
                "Final score": item["final_score"],
                "Eligible": "Yes" if item["eligible"] else "No",
                "Mandatory coverage": round(item["mandatory_coverage"], 3),
                "Preferred coverage": round(item["preferred_coverage"], 3),
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
        with st.expander(result["canonical_name"]):
            st.write({
                "match_type": result["match_type"],
                "keyword_score": result["keyword_score"],
                "semantic_score": result["semantic_score"],
                "fused_score": result["fused_score"],
                "missing": result["missing"],
                "reason_codes": result["reason_codes"],
                "evidence": result["evidence_text"],
            })

    st.subheader("Top 3 explanations")
    for explanation in explanations:
        st.markdown(f"**#{explanation['rank']} {explanation['candidate_id']}**")
        st.write(explanation["summary"])
        st.write({
            "strongest_matches": explanation["strongest_matches"],
            "missing_or_weak": explanation["missing_or_weak"],
            "evidence_refs": explanation["evidence_refs"],
            "reason_codes": explanation["reason_codes"],
        })


if __name__ == "__main__":
    main()