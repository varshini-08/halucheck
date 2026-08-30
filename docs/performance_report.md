# HaluCheck Performance Report

## Instrumentation

The pipeline records extraction, local FAISS, Wikipedia search, Wikipedia article retrieval, Wikipedia chunk ranking, NLI verification, and total timings in `AnalysisResult.comparison["timings"]`. `EvidenceRetriever.last_timings` and `WikipediaService.last_timings` expose retrieval details.

## Measured benchmark results

| Run | Samples | Average end-to-end time | Failures |
|---|---:|---:|---:|
| HaluEval 10, post-fix | 10 | 105.17s/sample | 0 |
| HaluEval 50, pre-list-fix | 50 | 62.20s/sample | 0 |
| HaluEval 100 | not completed | not available | not available |

## Wikipedia before/after

For HaluEval sample `1964`, the saved pre-optimization hybrid run took 56.71s and the optimized run took 28.99s. Observed reduction: 48.87%. This is one end-to-end observation and is affected by model loading, network state, and cache state; it is not a universal retrieval-only guarantee.

The deterministic fake-API repeat check made 2 HTTP calls for the first search/article lookup and 0 additional HTTP calls for the normalized repeated query. Wikipedia query, article, and ranking caches are now active.

## Main bottleneck

The earlier hybrid 10-sample comparison averaged 150.44s/sample, compared with 20.51s/sample for local-KB-only and 12.96s/sample for NLI-only. Live Wikipedia requests and transformer inference dominate wall time. The optimization retains Wikipedia and avoids it when local similarity is sufficient.
