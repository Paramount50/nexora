# Tech Stack — Smart Shortlisting Engine

## Language
Python 3 — best library support for both NLP/embeddings and PDF parsing; all three people can
work in one language, which matters more than usual with a 5-hour clock.

## By module

| Module | Library | Why |
|---|---|---|
| PDF parsing | `pdfplumber` or `PyMuPDF` (`fitz`) | Reliable text + layout extraction; PyMuPDF handles multi-column resumes better |
| Keyword matching | `rapidfuzz` | Fast fuzzy string matching, catches typos and phrasing variants (e.g. "JS" vs "JavaScript") |
| Skills taxonomy | Static JSON file | No external API/dependency; ~300–500 curated terms + aliases is enough for one JD family |
| Semantic matching | `sentence-transformers` (`all-mpnet-base-v2`, or `all-MiniLM-L6-v2` if speed is tight) | Pretrained sentence embeddings, no training needed, runs locally |
| Similarity | `scikit-learn` (`cosine_similarity`) or `numpy` dot product | Standard, fast for 18 resumes |
| Explanation polish (optional) | Any LLM API | Wording only — never the actual scoring |
| Demo UI | `streamlit` | Fastest way to get a ranked table + score breakdown on screen with minimal code |
| Bonus: recruiter chat | LLM API + precomputed rankings/explanations as context | Answers comparison questions without re-deriving scores |

## Setup

```bash
python -m venv venv
source venv/bin/activate          # or venv\Scripts\activate on Windows

pip install pdfplumber PyMuPDF rapidfuzz sentence-transformers scikit-learn streamlit
```

If using an LLM API for explanation polish or the bonus chat layer, add the relevant SDK
(e.g. `pip install anthropic` or `pip install openai`) and keep the API key in an environment
variable, not committed to the repo.

## Notes
- `all-mpnet-base-v2` is more accurate than MiniLM but slower to load; with only 18 resumes and a
  handful of JD lines, either works comfortably within the time budget — prefer mpnet unless
  first-run model download time becomes a problem.
- Keep the skills taxonomy and fusion-weight config as plain JSON files (see `scheme.md`) so
  they're editable without touching code.
- No database needed — everything fits in memory for a single JD + 18 resumes.
