# Matched GTR vs MiniLM Comparison

Dataset: `data/halu_eval/general_data.json`; seed: 42; matched sample IDs: 10/10.

| Configuration | Accuracy | Precision | Recall | F1 | TP | TN | FP | FN | Successful | Failed | Avg latency |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| GTR paper mode (768d) | 0.70 | 0.00 | 0.00 | 0.00 | 0 | 7 | 1 | 2 | 10 | 0 | 8.8605 s |
| MiniLM current mode (384d) | 0.80 | 0.00 | 0.00 | 0.00 | 0 | 8 | 0 | 2 | 10 | 0 | 9.5497 s |

MiniLM scored higher on this small matched run. The configurations differ in retrieval mode, so this is not a causal claim of embedding-model superiority.
