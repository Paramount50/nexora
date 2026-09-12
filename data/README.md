# Synthetic Dataset

`mock_resumes.json` contains 120 deterministic, fictional resume records in the
updated contract from `docs/scheme.md`. The profiles deliberately cover strong,
partial, adjacent, and weak matches for the Junior Full Stack Developer
Intern job description.

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

Regenerate both files with:

```text
python data/generate_mock_dataset.py
```

These records are synthetic test fixtures, not real applicant data. Replace
them with consented and anonymized resumes before making product decisions.
