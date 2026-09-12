from __future__ import annotations

import sys
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.evaluation.jd_bias import flag_jd_bias
from src.explanations.recruiter_chat import answer_recruiter_question, answer_with_gemini
from src.matching.ranker import rank_candidates
from src.pipeline import rank_documents
from src.parsing.jd_loader import extract_jd_text, extract_requirements
from src.parsing.resume_loader import load_resume

app = FastAPI(title="Nexora API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
RANKING_CACHE: dict[str, dict[str, Any]] = {}
CURRENT_RANKINGS: list[dict[str, Any]] = []
FRONTEND_DIST = ROOT / "frontend" / "dist"


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    grounded: bool = True


def parse_upload(upload: UploadFile, directory: Path) -> Path:
    filename = Path(upload.filename or "upload.txt").name
    path = directory / filename
    path.write_bytes(upload.file.read())
    return path


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/analyze")
def analyze(
    jd: UploadFile = File(...),
    resumes: list[UploadFile] = File(...),
    mode: str = Form("hybrid"),
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        jd_path = parse_upload(jd, root)
        jd_text = extract_jd_text(jd_path)
        requirement_data = extract_requirements(jd_text)
        candidates = [load_resume(parse_upload(resume, root)) for resume in resumes]
        fusion_config = fusion_for_mode(mode)
        semantic_engine = None
        semantic_enabled = False
        if mode != "keyword":
            semantic_engine = load_semantic_engine()
            semantic_enabled = semantic_engine is not None
        rankings = rank_documents(
            candidates,
            requirement_data["requirements"],
            semantic_engine=semantic_engine,
            fusion_config=fusion_config,
        )
        CURRENT_RANKINGS.clear()
        CURRENT_RANKINGS.extend(rankings)
        for item in rankings:
            RANKING_CACHE[item["candidate_id"]] = item
        return {
            "job": requirement_data,
            "candidate_count": len(rankings),
            "rankings": rankings,
            "bias_findings": flag_jd_bias(jd_text),
            "mode": mode,
            "semantic_enabled": semantic_enabled,
        }


@app.post("/api/rank")
def rank(
    requirements: str = Form(...),
    resumes: list[UploadFile] = File(...),
) -> dict[str, Any]:
    import json

    requirement_data = json.loads(requirements)
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        candidates = [load_resume(parse_upload(resume, root)) for resume in resumes]
        rankings = rank_candidates(candidates, requirement_data["requirements"])
        for item in rankings:
            RANKING_CACHE[item["candidate_id"]] = item
        return {"rankings": rankings}


@app.get("/api/candidate/{candidate_id}")
def candidate(candidate_id: str) -> dict[str, Any]:
    candidate_data = RANKING_CACHE.get(candidate_id)
    if candidate_data is None:
        return {"error": "Candidate not found", "candidate_id": candidate_id}
    return candidate_data


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    answer = answer_with_gemini(request.question, CURRENT_RANKINGS)
    return ChatResponse(answer=answer or answer_recruiter_question(request.question, CURRENT_RANKINGS))


def fusion_for_mode(mode: str) -> dict[str, float]:
    """Return the frontend-selectable score fusion configuration."""
    if mode == "keyword":
        return {"keyword_weight": 0.90, "semantic_weight": 0.0, "bm25_weight": 0.0, "evidence_strength_weight": 0.10}
    if mode == "semantic":
        return {"keyword_weight": 0.0, "semantic_weight": 0.85, "bm25_weight": 0.0, "evidence_strength_weight": 0.15}
    return {"keyword_weight": 0.40, "semantic_weight": 0.35, "bm25_weight": 0.15, "evidence_strength_weight": 0.10}


@lru_cache(maxsize=1)
def load_semantic_engine():
    """Load the embedding model once, while keeping lexical ranking available."""
    try:
        from src.matching.semantic_engine import SentenceTransformerEmbedder, SemanticEngine

        return SemanticEngine(SentenceTransformerEmbedder("all-MiniLM-L6-v2"))
    except Exception:
        # A missing model or offline environment should not prevent the core
        # keyword/BM25 ranking and evidence review from working.
        return None


if FRONTEND_DIST.exists():
    assets = FRONTEND_DIST / "assets"
    if assets.exists():
        app.mount("/assets", StaticFiles(directory=assets), name="assets")

    @app.get("/", include_in_schema=False)
    def frontend_index() -> FileResponse:
        return FileResponse(FRONTEND_DIST / "index.html")

    @app.get("/{path:path}", include_in_schema=False)
    def frontend_route(path: str):
        if path.startswith("api/"):
            return JSONResponse({"detail": "Not found"}, status_code=404)
        requested = FRONTEND_DIST / path
        if requested.is_file() and FRONTEND_DIST in requested.parents:
            return FileResponse(requested)
        return FileResponse(FRONTEND_DIST / "index.html")
