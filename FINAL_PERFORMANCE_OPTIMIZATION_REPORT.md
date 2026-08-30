# Final Performance Optimization Report

## Problem and root cause

Observed runs varied from approximately 18 to 64+ seconds. The current environment does not preserve the original 64-second stage trace, so a causal claim for the slow run is not invented. The pipeline already caches the NLI model/tokenizer and batches inference; the remaining variability is most likely retrieval/model warm-up and configured-source/network conditions.

## Implemented

- Added transparent support, contradiction, neutral/unverified, hallucination, and evidence-coverage rates to API metrics.
- Added NLI tokenization timing separate from inference timing.
- Preserved process-level NLI caching, batching, inference mode, configured device, evidence limits, and bounded retrieval concurrency.
- Preserved claim filtering and malformed duplicate-term cleanup.
- Wikipedia retrieval uses complete claims and rejects low-similarity passages using `EVIDENCE_RELEVANCE_THRESHOLD`.
- Provider status refresh remains bounded and does not continuously poll during analysis.

## Measured validation

- Live Groq Earth analysis previously completed in approximately **18.14–18.39 seconds** with four claims.
- Focused NLI/Groq/extraction regression tests: **18 passed**.
- Python compilation: **PASS**.
- React production build: **PASS**.
- API smoke tests: **PASS**.
- No API credentials found in frontend source/build/report files.

## Verification semantics

Neutral claims remain neutral and are not counted as hallucinations. API metrics now expose `hallucination_rate`, `support_rate`, `neutral_rate`, and `evidence_coverage` independently so the UI/API can distinguish “not contradicted” from “proven.”

## Limitations

- A reproducible three-run cold/warm benchmark with configured evidence sources is still required to explain the historical 64-second run precisely.
- Optional external adapters are not configured in this environment, so live evidence relevance and NLI timing are limited.
- Browser-based visual/manual testing and GitHub push were not performed.
