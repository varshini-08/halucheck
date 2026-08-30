# Final Performance and Evidence Fix Report

## Implemented

- Added configurable `EVIDENCE_RELEVANCE_THRESHOLD` (default `0.55`) to Wikipedia semantic ranking. Low-similarity passages are now rejected instead of being presented as primary evidence.
- Wikipedia fallback already searches with the full factual claim, avoiding entity-only disambiguation results such as generic “Newton” pages.
- Added duplicate-term cleanup to atomic fact normalization to prevent malformed claims such as repeated possessives/terms introduced by dependency-span reconstruction.
- Preserved NLI, source routing, FAISS, history, dashboard, and evidence scoring behavior.

## Validation

- Retrieval, Wikipedia, and extraction regression tests: **20 passed**.
- Prior complete suite: **70 passed, 1 skipped**; stale Windows pytest temporary directories can cause collection cleanup errors.
- Python compilation: **PASS**.
- React build: **PASS**.
- API smoke tests: **PASS**.
- Live Groq Earth analysis previously measured around **18 seconds** with four factual claims; the reported 178–361 second runs did not include reproducible stage timing payloads.

## Evidence behavior

Evidence below the configured semantic threshold is omitted, so unsupported claims remain neutral rather than being “supported” by unrelated text. If no sufficiently relevant evidence remains, the existing classifier returns neutral.

## Remaining limitations

- A configured external-source run is required to measure NLI timings and inspect cross-source evidence quality; the current environment has no optional external adapters configured.
- Browser-based manual validation and a three-run cold/warm benchmark were not performed automatically.
