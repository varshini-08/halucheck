# Optimization Report

Existing safe optimizations include process-level model caching, batched NLI,
FAISS index persistence, embedding/retrieval caches, local-first Wikipedia
fallback, normalized cache keys, and duplicate-query elimination.

Run `python -m evaluation.profile_pipeline --dataset data/halu_eval/general_data.json --sample-index 0` to collect a fresh measured profile. The profiler does not generate Groq responses. Stage values that are not separately instrumented remain `null`; no timings are estimated.

The repository already records one measured repeatable optimization sample in
`README.md` (56.71s before vs 28.99s after). That is one observed run, not a
general performance guarantee. Prediction-equivalence validation remains the
required gate for any future optimization.
