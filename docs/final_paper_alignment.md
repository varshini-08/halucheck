# Final Paper Alignment

Validation date: 2026-08-30. The project is **PARTIAL / PAPER-INSPIRED**, not an exact reproduction.

| Component | Paper specification | HaluCheck implementation | Status | Evidence |
|---|---|---|---|---|
| Atomic decomposition | Atomic claims; exact implementation details unavailable | spaCy dependency-aware extraction | PARTIAL MATCH | `extraction/atomic_fact_extractor.py` |
| Retrieval model | GTR-T5-base | Isolated `sentence-transformers/gtr-t5-base` mode | CLOSE MATCH | GTR 768d smoke/index validation |
| Evidence retrieval | Corpus and ranking details incompletely public | Local Wikipedia-style corpus, optional Wikipedia fallback | PARTIAL MATCH | `knowledge_base/`, retriever tests |
| Entailment/NLI | NLI decision process | DeBERTa-v3 MNLI FEVER/ANLI verifier | PARTIAL MATCH | `verification/nli_verifier.py`; current cache limitation recorded |
| Aggregation | Exact aggregation rule incomplete | Documented application policy | PARTIAL MATCH | `evaluation/paper_modes.py` |
| Baselines | Paper-specific baseline protocol | Gemini incomplete; SelfCheckNLI lacks required multi-response data | NOT REPRODUCIBLE | `results/baselines/` |
| Evaluation dataset | HaluEval general data | Local HaluEval general dataset | CLOSE MATCH | `data/halu_eval/general_data.json` |
| Metrics | Standard classification metrics | Programmatic confusion-matrix metrics | EXACT MATCH | `evaluation/metrics.py` |

The completed GTR experiment is 10/10 successful records, accuracy 0.70, TP 0, TN 7, FP 1, FN 2. This is a small operational comparison and does not establish that GTR is superior to MiniLM. GTR 50/100 experiments are not run.
