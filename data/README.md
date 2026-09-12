# Synthetic Dataset

`mock_resumes.json` contains 120 deterministic, fictional resume records in the
updated contract from `docs/scheme.md`. The profiles deliberately cover strong,
partial, adjacent, and weak matches for the Junior Full Stack Developer
Intern job description. Keep this fixture for development and regression
tests; it is no longer the primary evaluation input.

The dataset is organized at the dataset level as:

```json
{
  "job_description": { ... },
  "candidates": [
    {
      "candidate_id": "candidate_001",
      "candidate_name": "Aarav Sharma",
      "sections": { ... },
      "evidence": [ ... ]
    }
  ]
}
```

This keeps the mock data aligned to the requirement-level evidence model and
with the `eligibility` / `fit` split in the ranking design.

`mock_labels.json` contains evaluation-only fit bands. It is kept separate
from the parsed resume contract so ranking code cannot accidentally use the
expected answer as an input feature.

`mock_requirements.json` provides the synthetic JD requirements used during
development. It is a fixture for the matching pipeline, not a replacement for
the requirements extracted from the future runtime JD.

Regenerate both files with:

```text
python data/generate_mock_dataset.py
```

These records are synthetic test fixtures, not real applicant data. Replace
them with consented and anonymized resumes before making product decisions.

Place the supplied PDF/DOCX files under `data/runtime/` as described in
`data/runtime/README.md`. The extraction pipeline should read those files and
produce the same candidate/evidence contract used by the mock fixture.

The `dummy_resumes/Dummy Resumes/` folder currently contains 220 physical
files: 122 DOCX files, 54 PDF files, and 22 TXT/XML pairs. Some files are
alternate representations or variants of the same role-based resumes, so the
pipeline must not treat the file count as the candidate count.

The current loader processes the 22 XML files as a structured parser fixture.
The XML representation preserves section structure and its matching TXT file
is a fallback. Generate that initial structured subset with:

```text
python src/parsing/resume_loader.py
```

This writes `dummy_candidates.json`, which is an intermediate parser fixture
for matching and extraction tests. The next parsing step is to add DOCX and
PDF ingestion, then build a manifest to identify duplicate or alternate
representations before ranking all unique candidates.

Generate the conservative file manifest with:

```text
python src/parsing/manifest.py
```

This writes `dummy_manifest.json`. It groups identical normalized filenames and
flags multi-format groups for review; it does not merge candidates
automatically.
