# Final Optimization Report

## Code-level optimizations

Model caching, batched NLI, persistent FAISS loading, embedding/retrieval
caching, local-first retrieval, Wikipedia fallback caching, and duplicate-query
elimination are implemented without changing production models or policy.

## Controlled measurement

Run:

`python -m evaluation.performance_validation --dataset data/halu_eval/general_data.json --sample-index 0`

This produces `results/performance/final_validation.json` with measured cold and
warm passes using the same original response. No before/after speed percentage is
claimed until both comparable runs are actually completed.

## Limitations

Per-stage extraction/NLI timings are only reported where production hooks expose
them. GTR and 100-sample performance remain unavailable until their experiments
complete. Historical 10/50 results are preserved and are not overwritten.
