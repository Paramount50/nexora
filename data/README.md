# Synthetic Dataset

`mock_resumes.json` contains 120 deterministic, fictional resumes in the
contract from `docs/scheme.md`. The profiles deliberately cover strong,
partial, adjacent, and weak matches for the Junior Full Stack Developer
Intern job description.

`mock_labels.json` contains evaluation-only fit bands. It is kept separate
from the parsed resume contract so ranking code cannot accidentally use the
expected answer as an input feature.

Regenerate both files with:

```text
python data/generate_mock_dataset.py
```

These records are synthetic test fixtures, not real applicant data. Replace
them with consented and anonymized resumes before making product decisions.