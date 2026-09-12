"""Streamlit demo for the evidence-first ranking pipeline."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.explanations.explanation import explain_top_candidates
from src.pipeline import run_pipeline


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


@st.cache_data(show_spinner=False)
def load_keyword_ranking() -> list[dict]:
    return run_pipeline(DATA_DIR)


def main() -> None:
    st.set_page_config(page_title="Nexora Resume Ranking", layout="wide")
    st.title("Nexora Resume Ranking")
    st.caption("Evidence-first candidate ranking over the synthetic development dataset")

    rankings = load_keyword_ranking()
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