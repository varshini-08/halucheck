# Final Validation Report

Validation date: 2026-08-30

## Newly validated

| Component | Result | Evidence |
|---|---|---|
| Test suite | PASS | `python -m pytest -q`: 62 passed, 1 skipped; `python -m pytest -q tests`: 62 passed |
| Compilation | PASS | Requested packages compile without errors |
| MiniLM retrieval | PASS | Cached `all-MiniLM-L6-v2`, 384 dimensions; separate 7-vector FAISS index |
| GTR retrieval | PASS | Cached `sentence-transformers/gtr-t5-base`, 768 dimensions; separate 7-vector FAISS index |
| GTR offline smoke | PASS | `python scripts/test_gtr.py --offline` and `python -m scripts.gtr_offline_smoke` |
| GTR HaluEval experiment | VALIDATED | 10/10 successful; accuracy 0.70; TP 0, TN 7, FP 1, FN 2 |
| Streamlit startup | PASS | `python -m streamlit run app.py --server.headless true --server.port 8503`; HTTP 200 |
| Security scan | PASS WITH SCOPE | `.env` is ignored; no literal provider-secret pattern outside excluded `.env`/logs |
| Groq connectivity | PASS | One controlled request succeeded using the local `.env` key; no key or response content recorded |

## Current limitations found

- The prior NLI limitation was fixed in the validation script: `python scripts/test_nli_model.py --offline` now loads `MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli` from its local snapshot without a network fallback.
- Gemini integration remains implemented, but its 10-attempt artifact contains only one non-error prediction and nine quota-limited errors. It is **INCOMPLETE**, not a valid 10-sample baseline.
- Streamlit startup was verified, but manual browser interaction and screenshots were not performed in this headless validation environment.
- Cost analysis is **NOT VERIFIED**: no measured token usage plus authoritative price record is available locally.

## Test-environment diagnosis

In the restricted sandbox, pytest cannot remove workspace temporary directories such as `.pytest-tmp`; this produces 11 fixture setup errors after 51 tests pass. The same commands run with normal Windows permission complete successfully. This is an environment permission issue, not an application-test failure. The project keeps the explicit workspace-local pytest temporary configuration in `pytest.ini` because the global temporary directory is also restricted here.
