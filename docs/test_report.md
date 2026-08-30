# HaluCheck Test Report

## Final completed suite

Command:

```text
python -m pytest -q
```

Result: `55 passed, 1 skipped`, with three existing dependency deprecation warnings from spaCy/FAISS bindings. The skipped module is the manual Groq connectivity check.

## Coverage areas

- Atomic fact extraction and regression cases
- Entity detection and matching
- FAISS construction, persistence, ranking, corruption, and missing files
- Wikipedia caching, ranking, invalid responses, timeout/failure fallback
- Groq input/error handling
- DeBERTa adapter label normalization and fact classification
- Hallucination severity policy
- HaluEval loader, benchmark runner, metrics, and confusion matrix
- Comparative evaluation and shared sample IDs
- Streamlit/dashboard import and response rendering helpers
- Numbered/bulleted list and Markdown-table source-unit extraction regressions
- Optional GTR retrieval profile and paper preflight

## Focused validation

Retrieval-focused tests passed 10/10 after the optimization. NLI/classification tests passed 6/6. Comparative/benchmark tests passed 3/3 in the latest focused run.

## Residual test gap

A browser-driven Streamlit interaction test was not run. The Streamlit health endpoint returned `200 ok`; the real DeBERTa model was exercised through controlled semantic checks and a complete pipeline sample, while most unit tests use deterministic doubles to remain fast and reproducible.
