# Judge Question Runbook

## Why not use one LLM score?
The ranking engine is deterministic and auditable. It extracts requirements and resume evidence, combines lexical and semantic signals, applies mandatory eligibility rules, and stores the evidence behind every result. An LLM may polish wording, but it is not authoritative for scoring.

## How are exact and related matches different?
Exact matches require the canonical skill literally. Aliases cover controlled forms such as `NodeJS` and `Node.js`. Related technologies such as Express.js and Node.js receive supporting credit but are not treated as equivalent.

## How are false positives controlled?
Matching uses token boundaries, explicit aliases, conservative fuzzy matching, and separate related-skill handling. Examples such as Java versus JavaScript, React versus React Native, and ambiguous bare `Node` are tested explicitly.

## How are mandatory requirements handled?
Eligibility is separate from general fit. A candidate who misses a required requirement cannot outrank an eligible candidate solely because of broad preferred-skill coverage.

## What evidence supports an explanation?
Every explanation references structured evidence IDs, source text, section, and provenance where available. Missing requirements are reported instead of being inferred.

## Why use both keyword and semantic matching?
Keyword matching captures explicit technology evidence. Semantic retrieval captures relevant context when terminology differs. They remain separate and are fused at the requirement level so either signal can be inspected.

## Are the weights final?
No. The current values are an initial baseline. They will be evaluated against the supplied JD and resumes plus a human reference ranking before final tuning.

## What happens with poor PDFs?
PyMuPDF is used first. Low-text pages trigger an optional Tesseract OCR fallback. Page numbers and evidence positions are retained when available.

## What are the current limitations?
The synthetic fixtures are development data, not the final benchmark. They contain repeated profiles and categorical fit bands, so final ranking decisions must be checked against the actual supplied resumes.
