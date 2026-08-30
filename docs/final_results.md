# Final Results

Validated results are stored in `results/halueval_10/`, `results/halueval_50/`, and `results/halueval_comparison/`.

| Run | Accuracy | Precision | Recall | F1 | TP | TN | FP | FN | Failed | Avg latency |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| HaluEval 10 | 0.70 | 0.00 | 0.00 | 0.00 | 0 | 7 | 1 | 2 | 0 | 105.1703s |
| HaluEval 50 | 0.80 | 0.25 | 0.125 | 0.1667 | 1 | 39 | 3 | 7 | 0 | 62.1952s |

Comparative values are available in `results/halueval_comparison/comparison.csv`. GTR, SelfCheckNLI, LLM baseline, and 100-sample results are not claimed.
