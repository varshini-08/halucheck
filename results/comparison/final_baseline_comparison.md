# Final Baseline Comparison

| System | Samples | Successful | Accuracy | Precision | Recall | F1 | Status |
|---|---:|---:|---:|---:|---:|---:|---|
| HaluCheck MiniLM (10) | 10 | 10 | 70% | 0% | 0% | 0% | COMPLETE |
| HaluCheck MiniLM (50) | 50 | 50 | 80% | 25% | 12.5% | 16.67% | COMPLETE |
| HaluCheck MiniLM (100) | 100 | 99 | 80.81% | 0% | 0% | 0% | COMPLETE; 1 failed |
| HaluCheck GTR (10) | 10 | 10 | 80% | 0% | 0% | 0% | COMPLETE |
| Gemini LLM judge (10 attempted) | 10 | 6 | 83.33% | 0% | 0% | 0% | COMPLETE; 4 API failures |
| Groq LLM judge | N/A | N/A | N/A | N/A | N/A | N/A | NOT EXECUTED |
| SelfCheckNLI | N/A | N/A | N/A | N/A | N/A | N/A | NOT REPRODUCIBLE |

LLM-judge results are baselines and are not equivalent to the full HaluCheck
retrieval + NLI detector. Gemini metrics are from
`results/baselines/llm_gemini/metrics.json`.
