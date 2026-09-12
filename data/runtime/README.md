# Runtime Resume Inputs

Place the supplied job description and resume files here for local evaluation.

Suggested layout:

```text
data/runtime/
  job_description.pdf
  resumes/
    resume_01.pdf
    resume_02.pdf
    resume_03.docx
```

These files are runtime inputs and should not be committed if they contain
private or identifying applicant information. Add `data/runtime/` to the local
ignore rules when the files are copied into the workspace.

The parser should convert PDF and DOCX files into the shared candidate and
evidence contracts defined in `docs/scheme.md`. Keep `data/mock_resumes.json`
as a deterministic regression fixture for development tests.
