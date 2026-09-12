# Tech Stack — Hybrid Resume Shortlisting Engine

## Primary language
Python 3.11+

## Core libraries

| Area | Preferred stack | Reason |
|---|---|---|
| PDF extraction | PyMuPDF (`fitz`) | Fast, reliable PDF text extraction with page-level provenance |
| DOCX extraction | `python-docx` | Read supplied Word resumes while preserving paragraph order |
| OCR fallback | PaddleOCR or Tesseract | Only used when PyMuPDF output is poor |
| Data validation | Pydantic | Clean schemas for JD requirements, evidence, and ranking output |
| Text normalization | Python stdlib + regex | Deterministic cleanup of whitespace, bullets, weird formatting, and date noise |
| Keyword matching | RapidFuzz | Controlled fuzzy matching for alias and formatting variations |
| Lexical retrieval | BM25 | Strong explicit-match signal for technology and responsibility keywords |
| Semantic matching | Qwen3-Embedding-0.6B | Preferred embedding model for JD requirement vs evidence similarity |
| Fallback embedding | all-MiniLM-L6-v2 or all-mpnet-base-v2 | Used if the preferred model is unavailable or too slow |
| Similarity / ranking math | NumPy + scikit-learn | Cosine similarity, normalization, and score computations |
| Optional reranker | Qwen3-Reranker-0.6B | Used only on top retrieved evidence, not as the final system |
| API boundary | FastAPI | Optional if a clean backend boundary is useful |
| UI | React + Vite served by FastAPI | Best for a reliable hackathon demo |
| Storage | JSON first, SQLite only if persistence becomes useful | No Elasticsearch or vector DB needed |
| LLM usage | Optional explanation polish only | Never authoritative for scoring |

## Preferred model strategy
- Preferred embedding: Qwen3-Embedding-0.6B
- Preferred reranker: Qwen3-Reranker-0.6B
- Baseline comparison: sentence-transformer models if needed

Important:
- Do not assume the newest model is automatically best.
- Benchmark the selected model on the actual JD and resume data.
- Keep the final ranking system deterministic and auditable.

## Installation

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install pymupdf python-docx rapidfuzz pydantic numpy scikit-learn rank-bm25 fastapi uvicorn python-multipart
pip install sentence-transformers
```

If OCR is required:

```bash
pip install paddleocr
# or
pip install tesseract
```

If using an LLM for explanation wording only:

```bash
pip install openai
# or whichever API SDK is relevant
```

## Design principles
- No model training required.
- No Elasticsearch.
- No vector database for this dataset.
- No unnecessary microservices.
- No cloud infrastructure unless absolutely required.
- Keep the system small enough to understand and defend in a live judge walkthrough.

## Notes
- Use PyMuPDF first and only fall back to OCR if extraction quality is poor.
- Keep requirement and alias mappings in JSON rather than burying them in code.
- Persist only what helps the demo and explanation flow; the dataset is small enough for an in-memory pipeline.
