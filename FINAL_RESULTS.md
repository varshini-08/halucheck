# Final Results

## Validated results

| Experiment | Status | Evidence |
|---|---|---|
| HaluEval 10 | COMPLETED | `results/halueval_10/` |
| HaluEval 50 | COMPLETED | `results/halueval_50/` |
| HaluEval 100 | NOT EXECUTED | No validated output directory |
| NLI-only/local/hybrid comparison | COMPLETED | `results/halueval_comparison/` |
| GTR | NOT EXECUTED | `evaluation.paper_comparison` preflight; separate index unavailable |
| LLM-as-judge | NOT EXECUTED | No validated API run |
| SelfCheckNLI | BLOCKED | Single-response HaluEval data |
| Performance | COMPLETED | `results/performance/` and `evaluation.generate_performance` |
| Browser UI | NOT EXECUTED | Interactive browser unavailable |

## Existing measured metrics

The 10- and 50-sample metrics are retained from prior runs and independently checked against predictions and confusion matrices. No 100-sample, GTR, LLM, or SelfCheck metrics are invented.

## Reproduction

See `FINAL_COMPLETION_REPORT.md`, `evaluation.md`, and `paper_alignment_report.md` for exact commands and limitations.
