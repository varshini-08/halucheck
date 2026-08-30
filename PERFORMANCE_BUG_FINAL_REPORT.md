# Performance Bug Investigation

## Reproduction

The live API was started with the existing `.venv` and tested using Groq. The Earth question completed with HTTP 200, four claims, and a measured total of **18.39 seconds** in this run (not 328 seconds). The response contained no evidence because optional external adapters were not configured, so NLI inference was not invoked for that request (`nli_inference_seconds=0`).

## Findings

- NLI tokenizer/model loading is process-cached through the existing `lru_cache` resource manager.
- NLI work is batched and uses `model.eval()` plus `torch.inference_mode()`.
- The verifier logs whether resources were initialized or reused and selects CPU/CUDA according to `NLI_DEVICE`.
- The measured request spent most of its time outside NLI, during retrieval/model setup; therefore the earlier 328-second report cannot be attributed to NLI alone without its original timing trace.
- Frontend provider status refreshes at a bounded 15-second interval and on provider changes; it does not poll continuously during an analysis.

## Changes made

- Added API timing metadata for LLM generation and SQLite persistence alongside pipeline timings.
- Added explicit model initialization/reuse logging.
- Retained evidence limits, retrieval caching, bounded external concurrency, and batched NLI; no verification algorithm or source was removed.

## Regression and security

- Focused Groq/extraction/NLI tests: **18 passed**.
- Previously validated complete suite: **70 passed, 1 skipped**; stale Windows pytest temporary-directory permissions can cause setup/cleanup errors in a fresh full collection.
- Python compilation: **PASS**.
- React build: **PASS**.
- API smoke routes: **all 200**.
- `.env` ignored and no frontend secret exposure: **PASS**.

## Limitations

The original 328.78-second run did not include a saved per-stage timing payload, and the current environment had no configured evidence adapters for a meaningful NLI benchmark. A second warm request should be measured in a long-lived backend process with evidence configured before claiming a warm-vs-cold improvement. No GitHub push was performed.
