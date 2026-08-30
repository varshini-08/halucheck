# Final Results Table

| Configuration | Retriever | NLI | Samples | Accuracy | Precision | Recall | F1 | Failures | Status |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| HaluCheck current | MiniLM + hybrid fallback | DeBERTa-v3-MNLI | 10 | 0.70 | 0.00 | 0.00 | 0.00 | 0 | VALIDATED |
| HaluCheck current | MiniLM + hybrid fallback | DeBERTa-v3-MNLI | 50 | 0.80 | 0.25 | 0.125 | 0.1667 | 0 | VALIDATED |
| NLI-only | Response premise | DeBERTa-v3-MNLI | 10 | 0.70 | 0.00 | 0.00 | 0.00 | 0 | VALIDATED |
| Local KB | MiniLM local | DeBERTa-v3-MNLI | 10 | 0.80 | 0.50 | 0.50 | 0.50 | 0 | VALIDATED |
| Hybrid | MiniLM + Wikipedia | DeBERTa-v3-MNLI | 10 | 0.80 | 0.00 | 0.00 | 0.00 | 0 | VALIDATED |
| GTR | GTR-T5-base | DeBERTa-v3-MNLI | — | — | — | — | — | — | NOT RUN |
| SelfCheckNLI | Multiple responses required | NLI | — | — | — | — | — | — | BLOCKED |
| LLM judge | API-dependent | Groq | — | — | — | — | — | — | NOT RUN |

Only completed outputs are populated. Values are read from existing validated artifacts.
# Final Results Table

Only executed experiments are given numeric results.

| System | Retrieval | NLI | Accuracy | Precision | Recall | F1 |
|---|---|---|---:|---:|---:|---:|
| HaluCheck (10) | MiniLM/local+hybrid | DeBERTa-v3-MNLI | 70% | 0% | 0% | 0% |
| HaluCheck (50) | MiniLM/local+hybrid | DeBERTa-v3-MNLI | 80% | 25% | 12.5% | 16.67% |
| HaluCheck (100 attempted; 99 valid) | MiniLM/local+hybrid | DeBERTa-v3-MNLI | 80.81% | 0% | 0% | 0% |
| HaluCheck GTR | GTR-Base | DeBERTa-v3-MNLI | NOT AVAILABLE | NOT AVAILABLE | NOT AVAILABLE | NOT AVAILABLE |
| LLM-as-Judge | API dependent | Judge model | NOT AVAILABLE | NOT AVAILABLE | NOT AVAILABLE | NOT AVAILABLE |
| SelfCheckNLI | Multiple responses required | NLI | NOT AVAILABLE | NOT AVAILABLE | NOT AVAILABLE | NOT AVAILABLE |

Sources: `results/halueval_10/metrics.json`, `results/halueval_50/metrics.json`, and `results/halueval_100/metrics.json`.
