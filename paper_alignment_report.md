# HaluCheck Paper-Level Evaluation Status

Generated from the current repository audit. Metrics are never filled manually.

| Component | Paper | Current implementation | Status | Evidence |
|---|---|---|---|---|
| Retrieval | GTR-T5-base | Isolated optional GTR index/configuration | PARTIAL MATCH | `scripts/build_index.py --retrieval-mode paper`, `evaluation.paper_comparison` |
| Atomic decomposition | Paper-described atomic claims | Deterministic spaCy extractor; paper mode delegates to it | PARTIAL MATCH | `evaluation.paper_modes.PaperAtomicFactExtractor` |
| Entailment aggregation | Paper details not fully specified publicly | Isolated average-probability approximation | PARTIAL MATCH | `aggregate_paper_style` |
| HaluEval | General benchmark | Official `general_data.json` loader | MATCH | `evaluation.halu_eval_loader` |
| Metrics | Classification metrics | Programmatic metrics and confusion matrix | MATCH | `evaluation.metrics` |
| SelfCheckNLI | Multiple stochastic responses required | Explicitly unavailable for one-response general data | NOT IMPLEMENTED | `evaluation.baseline_runner` |
| LLM judge | Independent judge | Opt-in Groq baseline with normalized labels | PARTIAL MATCH | `evaluation.llm_baseline` |

The exact paper implementation cannot be claimed because the decomposition and
aggregation algorithms are not fully specified in the available methodology.

## Executed evidence

The current validated artifacts are `results/halueval_10` and `results/halueval_50`. GTR preflight reports the separate index is unavailable. No unexecuted experiment is represented as a result.
