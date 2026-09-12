# Demo Runbook

## Setup

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Run the automated checks:

```powershell
python -m pytest -q tests
```

## Launch

Build the React interface and run the single FastAPI server:

```powershell
npm --prefix frontend install
npm --prefix frontend run build
$env:PYTHONPATH = (Get-Location).Path
python -m uvicorn backend.main:app --reload
```

Open `http://localhost:8000`. FastAPI serves the built frontend and the `/api` endpoints from the same origin.

## Runtime demonstration

1. Select a scoring mode.
2. Upload one JD as PDF, DOCX, or TXT.
3. Upload the resume set as PDF, DOCX, TXT, or XML files.
4. Confirm the candidate count matches the uploaded set.
5. Show the ranking table and eligibility status.
6. Open a candidate to show requirement-level evidence.
7. Compare two candidates using the comparison table.
8. Show the top-three evidence-grounded explanations.
9. Explain one exact match, one related match, and one missing requirement.

## Judge walkthrough

- Start with the raw input files and extraction provenance.
- Show that keyword and semantic scores remain separate.
- Show why a candidate with a missing mandatory requirement is gated.
- Open the evidence behind a top match.
- Demonstrate a negative case such as React versus React Native or bare Node.
- State that weights are baseline values until human review of the official data.
