# Final Project Health

Scores are qualitative and evidence-based; no arbitrary percentage is assigned.

| Area | Assessment | Evidence |
|---|---|---|
| Functional correctness | Strong | Phase 1–4 tests and controlled extraction validation pass |
| Test coverage | Strong | 60 passed, 1 skipped |
| Retrieval reliability | Strong with external dependency | FAISS/Wikipedia tests pass; live network remains variable |
| NLI reliability | Validated contract | NLI tests and label/probability handling pass; live model is resource-dependent |
| Evaluation reliability | Strong for completed runs | 10/50 predictions and metrics independently agree |
| UI readiness | Application-ready, browser unverified | App import tests pass; no interactive browser session |
| Performance | Measured but model-bound | Existing timing artifacts; model initialization is the main observed cost |
| Security | Pass | `.env` ignored and repository audit found no secret patterns in artifacts |
| Reproducibility | Strong with documented prerequisites | `REPRODUCIBILITY_GUIDE.md` and fixed seeds |
| Paper alignment | Partial | GTR, SelfCheckNLI, and exact paper decomposition remain unavailable/underspecified |
