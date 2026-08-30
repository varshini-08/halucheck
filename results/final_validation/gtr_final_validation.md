# GTR Final Validation — 2026-08-30

| Check | Result |
|---|---|
| Model | PASS — `sentence-transformers/gtr-t5-base` |
| Embedding dimension | PASS — 768 |
| Paper index | PASS — `vector_db/gtr_base.index`, 7 vectors |
| Metadata | PASS — `gtr_base_metadata.pkl`, 7 records |
| Manifest | PASS — model, dimension, mode, and counts match |
| Offline smoke | PASS — `python scripts/test_gtr.py --offline` |
| Offline retrieval | PASS — `python -m scripts.gtr_offline_smoke`, 3/3 successful |
| MiniLM fallback | PASS — paper mode requires GTR and its separate index |
| Existing experiment | PASS — preserved GTR HaluEval 10: 10/10 successful, accuracy 0.70, TP 0, TN 7, FP 1, FN 2 |

The existing GTR evaluation was not regenerated.
