# Paper Comparison

| Paper component | Paper method | HaluCheck implementation | Status |
|---|---|---|---|
| Retrieval model | GTR-T5-base | MiniLM production default; isolated GTR mode | RESOURCE BLOCKED |
| Atomic decomposition | Paper-described atomic claims | Deterministic spaCy dependency rules | PARTIAL MATCH |
| Evidence retrieval | Retrieved supporting context | Local FAISS with Wikipedia fallback | PARTIAL MATCH |
| Entailment | NLI-based verification | DeBERTa-v3-MNLI | MATCH |
| Aggregation | Paper details incomplete | Existing production policy plus isolated approximation | PARTIAL MATCH |
| Dataset | HaluEval | Official general_data.json | MATCH |
| SelfCheckNLI | Multiple stochastic responses | Infrastructure only; one response per sample | NOT IMPLEMENTED |
| LLM baseline | Judge model | Opt-in Groq adapter | NOT IMPLEMENTED |
| Cost | Provider-dependent | Reports unavailable without verified pricing | PARTIAL MATCH |

This is paper-inspired, not an exact reproduction.
