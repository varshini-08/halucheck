# Final Reproduction Report

Validation date: 2026-08-30

## What was implemented and validated

HaluCheck implements atomic fact extraction, entity matching, MiniLM local-first FAISS retrieval with optional Wikipedia fallback, a separate GTR-T5-base paper mode, DeBERTa NLI integration, response-level classification, HaluEval evaluation, comparative evaluation, and a Streamlit interface.

- GTR model/index/offline smoke tests pass: GTR is 768-dimensional, uses only `vector_db/gtr_base.index`, and completed the preserved 10-sample experiment (10/10 successful, 70% accuracy).
- MiniLM loads offline at 384 dimensions and uses only `vector_db/vector.index`.
- The full automated suite passes: 62 passed, 1 skipped; the `tests` target passes 62 tests.
- Requested compilation passes without errors.
- Streamlit starts successfully and returns HTTP 200 in headless mode.

## What is not reproducible in the current environment

- The DeBERTa NLI model is cached and passes the explicit offline smoke command; no fallback model is used.
- Gemini’s detailed 10-attempt baseline is incomplete because nine attempts were rate/quota limited. No further API calls were made.
- SelfCheckNLI cannot be evaluated from the local HaluEval structure because there is only one response per prompt.
- Manual browser interaction, screenshots, and cost calculation are not claimed.

## Paper alignment

The project is **PARTIAL / PAPER-INSPIRED**, not an exact reproduction. GTR retrieval and standard classification metrics are closely matched, but the public paper does not supply enough detail to reproduce its exact atomic decomposition, evidence corpus, aggregation rule, or baseline protocol.

See `FINAL_SUBMISSION_STATUS.md` for the authoritative experimental matrix and `docs/final_paper_alignment.md` for component-level evidence.
