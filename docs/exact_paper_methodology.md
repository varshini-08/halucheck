# Exact Paper Methodology Audit

> **Current execution update (2026-08-28):** GTR is no longer unexecuted. The isolated local GTR model/index, offline smoke test, and controlled 2-/10-sample pipelines passed; the 10-sample GTR result is 0.70 accuracy (TP 0, TN 7, FP 1, FN 2). The project remains paper-inspired rather than an exact reproduction because the public decomposition and aggregation details are incomplete.

This project is paper-inspired, not an exact reproduction. The public methodology does not fully specify every implementation detail.

| Component | Published/required method | Current implementation | Status |
|---|---|---|---|
| Response generation | Paper-specific generation protocol | Groq `openai/gpt-oss-20b` for live UI; original HaluEval responses for evaluation | PARTIAL MATCH |
| Atomic decomposition | Atomic factual claims | Dependency-aware spaCy extractor | PARTIAL MATCH |
| Entity extraction | Not sufficiently specified | spaCy entities + RapidFuzz matching | NOT SPECIFIED |
| Retrieval | Semantic evidence retrieval | MiniLM production; isolated GTR paper mode | PARTIAL MATCH |
| GTR | `sentence-transformers/gtr-t5-base` | Builder/smoke test/index mode implemented, index unavailable | NOT EXECUTED |
| Knowledge base | Paper corpus details | Local Wikipedia-style JSON corpus | PARTIAL MATCH |
| NLI | Entailment/contradiction/neutral | DeBERTa-v3-MNLI | PARTIAL MATCH |
| Aggregation | Exact rule not fully specified | Existing policy plus isolated approximation | NOT SPECIFIED |
| Dataset | HaluEval | Official general dataset, 4,507 JSONL records | MATCH |
| Baselines | Paper-specific configurations | Infrastructure only; no valid runs | NOT EXECUTED |
| Metrics | Classification metrics | Programmatic accuracy/precision/recall/F1/confusion matrix | MATCH |
| Cost | Provider-specific | No verified pricing configured | NOT SPECIFIED |

Where the paper omits a reproducible algorithm, this project documents the closest defensible implementation rather than inventing an exact one.
