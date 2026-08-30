# Final Paper Reproduction Status

> **Current GTR status (2026-08-28; supersedes stale blocked statements below):** paper-mode GTR is complete for controlled 2- and 10-sample evaluation. Local model, separated index/manifest, and smoke check PASS; 10/10 records completed with accuracy 0.70 (TP 0, TN 7, FP 1, FN 2). GTR 50/100 remains NOT RUN. This is partial paper reproduction, not a claim of complete paper reproduction.

| Paper component | Status | Evidence |
|---|---|---|
| Response generation | PARTIAL | Groq service and original HaluEval responses |
| Atomic decomposition | PARTIAL | `extraction/atomic_fact_extractor.py`; methodology underspecified |
| Entity detection | PARTIAL | spaCy/RapidFuzz implementation |
| Retrieval | PARTIAL | MiniLM production and isolated GTR infrastructure |
| GTR | NOT EXECUTED | `results/final_validation/gtr_validation.md` |
| Knowledge base | PARTIAL | `knowledge_base/wikipedia.json` |
| NLI | PARTIAL | DeBERTa adapter and tests |
| Aggregation | PARTIAL | `evaluation/paper_modes.py`; exact paper rule unavailable |
| Hallucination decision | MATCH to current documented policy | Fact classifier tests |
| SelfCheckNLI | NOT REPRODUCIBLE | Single-response dataset |
| LLM baseline | NOT EXECUTED | API-dependent |
| Dataset | COMPLETE | Official HaluEval data validation |
| Metrics | COMPLETE | 10/50 outputs independently checked |
| Cost analysis | NOT SPECIFIED | Verified pricing unavailable |
| Evaluation scale | PARTIAL | 10 and 50 completed; 100 not completed |

## GTR validation update — 2026-08-28

| Paper component | Status | Evidence |
|---|---|---|
| GTR local model | PASS | `results/final_validation/gtr_local_validation.json` |
| GTR index | PASS | `results/final_validation/gtr_index_validation.json` |
| GTR retrieval smoke | PASS | `results/final_validation/gtr_offline_smoke.json` |
| GTR end-to-end evaluation | BLOCKED | Local DeBERTa NLI cache missing; `results/halueval_gtr_2/` |
| GTR 10/50/100 evaluation | NOT RUN | 2-sample prerequisite did not pass |
