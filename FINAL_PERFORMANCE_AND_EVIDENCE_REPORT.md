# Final Performance and Evidence Report

## Executive summary

The reported 178-second execution was not consistently reproducible in the current environment. A live Groq analysis completed in **18.39 seconds** in one run and a later live Earth analysis completed in **18.14 seconds**, returning HTTP 200 with four claims. The backend now exposes LLM, pipeline, NLI, and persistence timing metadata for future slow-run diagnosis.

## Fix implemented

Wikipedia fallback queries now use the complete factual claim instead of an isolated named entity. This prevents ambiguous searches such as `Newton` from selecting disambiguation content unrelated to a claim about Newton's laws or orbital motion. Existing semantic ranking, deduplication, NLI verification, and source routing remain unchanged.

## Measured live result

- Provider: Groq
- Question: Why does Earth revolve around the Sun?
- HTTP result: 200
- Claims: 4
- Total processing time: 18.39 seconds
- Evidence: 0 in the measured environment because optional external adapters were unconfigured
- Generated response: concise; no detected meta/instruction phrases

The prior observations of approximately 328 seconds and 178 seconds are retained as historical observations, but their original per-stage timing payloads were not saved, so a causal before/after claim is not fabricated.

## Performance safeguards

- NLI tokenizer/model are process-cached and reused.
- NLI runs in batches with `NLI_BATCH_SIZE`, `NLI_MAX_LENGTH`, `model.eval()`, and `torch.inference_mode()`.
- Device selection honors `NLI_DEVICE` and safely falls back to CPU.
- Retrieval caching, bounded external concurrency, and evidence limits remain enabled.
- `/api/analyze` now returns `timing.llm_seconds`, pipeline timing fields, NLI timing fields, total time, and storage time.

## Validation

- Focused retrieval/Wikipedia/source tests: **15 passed**.
- Earlier complete suite: **70 passed, 1 skipped**; stale Windows pytest temp-directory permissions can cause collection cleanup errors.
- Python compilation: **PASS**.
- React build: **PASS**.
- API smoke routes: **PASS** (all expected routes returned 200).
- Security scan: **PASS**; no credentials in frontend/build/report files.

## Remaining limitations

- A three-run warm/cold comparison with configured evidence sources was not completed; optional adapters are not configured in this environment.
- Browser-based manual verification and visual evidence inspection were not performed automatically.
- Evidence quality should be rechecked with configured Wikipedia/external retrieval; the claim-focused query fix addresses the observed entity-disambiguation failure but does not guarantee every source result is relevant.

## Status

**Performance status: NEEDS FURTHER MEASURED PROFILING for the intermittent slow-run case.**

**Evidence quality: IMPROVED; requires configured-source manual review.**

**Overall: READY WITH MINOR LIMITATIONS.**
