# HaluCheck — Final Submission Status

Validation date: 2026-08-30

## Status summary

| Area | Status | Evidence |
|---|---|---|
| Project / core system | IMPLEMENTED | Extraction, retrieval, NLI integration, classification, evaluation, and UI code are present |
| Paper retrieval | GTR-T5-base PASS | `sentence-transformers/gtr-t5-base`, offline 768d model and isolated index pass |
| GTR experiment | 10-sample PASS | 10/10 successful; accuracy 0.70; TP 0, TN 7, FP 1, FN 2 |
| MiniLM comparison | 10-sample PASS | Matched records; accuracy 0.80; TP 0, TN 8, FP 0, FN 2 |
| HaluEval | VALIDATED | 10/10, 50/50, and 99/100 valid MiniLM result records preserved |
| NLI | PASS | `python scripts/test_nli_model.py --offline` loads the cached DeBERTa model without a network fallback |
| Groq | IMPLEMENTED | Provider code and tests exist; no new live request made |
| Gemini | INTEGRATION IMPLEMENTED; BASELINE INCOMPLETE | 1 non-error prediction / 10 attempts; remaining attempts are quota-limited |
| SelfCheckNLI | NOT REPRODUCIBLE | Current official data has one response per prompt, not multiple stochastic responses |
| Streamlit | STARTUP PASS; MANUAL PENDING | Headless server returned HTTP 200; no screenshots or interactive claims |
| Security | PASS WITH SCOPE | `.env` ignored; no literal provider-secret pattern found outside excluded secret/log files |
| Tests | PASS | Full: 62 passed, 1 skipped. `tests`: 62 passed |
| Compilation | PASS | Requested modules compile without errors |
| Paper reproduction | PARTIAL / PAPER-INSPIRED | Exact decomposition and aggregation specifications are not sufficiently public |

## Authoritative experimental matrix

Metrics are read from the preserved result artifacts. “Successful” excludes records labelled `error`.

| Configuration | Dataset | Attempted | Successful | Failed | Accuracy | Precision | Recall | F1 | TP | TN | FP | FN | Avg latency | Status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| HaluCheck + MiniLM, matched comparison | HaluEval general | 10 | 10 | 0 | 0.80 | 0.00 | 0.00 | 0.00 | 0 | 8 | 0 | 2 | Not recorded in comparison summary | VALIDATED |
| HaluCheck + GTR | HaluEval general | 10 | 10 | 0 | 0.70 | 0.00 | 0.00 | 0.00 | 0 | 7 | 1 | 2 | 8.8605 s | VALIDATED |
| NLI-only | HaluEval general | 10 | 10 | 0 | 0.70 | 0.00 | 0.00 | 0.00 | 0 | 7 | 1 | 2 | 9.3595 s | EXISTING ARTIFACT |
| Local KB | HaluEval general | 10 | 10 | 0 | 0.80 | 0.50 | 0.50 | 0.50 | 1 | 7 | 1 | 1 | 8.1873 s | EXISTING ARTIFACT |
| Hybrid | HaluEval general | 10 | 10 | 0 | 0.80 | 0.00 | 0.00 | 0.00 | 0 | 8 | 0 | 2 | 92.8701 s | EXISTING ARTIFACT |
| HaluCheck + MiniLM | HaluEval general | 50 | 50 | 0 | 0.80 | 0.25 | 0.125 | 0.1667 | 1 | 39 | 3 | 7 | 62.1952 s | VALIDATED |
| HaluCheck + MiniLM | HaluEval general | 100 | 99 | 1 | 0.8081 | 0.00 | 0.00 | 0.00 | 0 | 80 | 0 | 19 | 8.7346 s | VALIDATED; metrics over 99 records |
| Gemini baseline | HaluEval general | 10 | 1 | 9 | 1.00 | 0.00 | 0.00 | 0.00 | 0 | 1 | 0 | 0 | 16.0109 s | INCOMPLETE — quota limited |
| Groq baseline | — | — | — | — | — | — | — | — | — | — | — | — | — | NOT RUN |
| SelfCheckNLI | HaluEval general | — | — | — | — | — | — | — | — | — | — | — | — | NOT REPRODUCIBLE |

The 10-record MiniLM/GTR comparison does not demonstrate model superiority. A stale aggregate Gemini comparison artifact conflicts with the detailed, later quota-limited run; it is excluded from this matrix rather than treated as a valid baseline.

## Reproduction commands

```powershell
python -m pytest -q
python -m pytest -q tests
python -m compileall -q app.py services extraction verification evaluation retrieval analysis visualization scripts
python scripts/test_gtr.py --offline
python -m scripts.gtr_offline_smoke
python -m streamlit run app.py --server.headless true
```

For a complete offline live verification, restore the DeBERTa model cache first. Do not attempt repeated Gemini retries while quota remains exhausted.
