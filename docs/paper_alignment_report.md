# HaluCheck Paper Alignment Report

| Area | Status | Evidence |
|---|---|---|
| Overall response -> facts -> evidence -> NLI -> explanation flow | PARTIAL MATCH | Same broad pipeline is connected in `services/analysis_service.py`. |
| Atomic decomposition | DIFFERENT | Current extractor is spaCy/rule based; paper describes InstructGPT-style 8-shot decomposition. |
| Dense retrieval | DIFFERENT | Current default is `all-MiniLM-L6-v2`; optional paper mode targets `sentence-transformers/gtr-t5-base`, but its separate model/index is not currently available. |
| FAISS retrieval | PARTIAL MATCH | Current normalized inner-product FAISS index provides top-k evidence. |
| Wikipedia source | PARTIAL MATCH | Current system uses a local corpus plus live Wikipedia fallback. |
| NLI model | PARTIAL MATCH | Current DeBERTa-v3 MNLI-FEVER-ANLI is an NLI model, but exact paper checkpoint/settings differ. |
| Entailment aggregation | DIFFERENT | Current FactClassifier uses a 0.70 strong-result threshold and evidence-level precedence, not exact average entailment. |
| Hallucination decision | PARTIAL MATCH | Contradicted facts are hallucinations; neutral facts are uncertain and not silently treated as factual. |
| Visualization | PARTIAL MATCH | Original response is preserved and fact spans are highlighted. |
| HaluEval | PARTIAL MATCH | Reproducible 10/50/100 sampling is implemented; only small development samples were run. |
| Paper baselines | NOT IMPLEMENTED | SelfCheckNLI and prompt-based GPT baseline are not present; the existing comparative runner is an internal NLI/local/hybrid comparison. |
| Cost analysis | NOT IMPLEMENTED | Provider cost accounting is not implemented. |
| Paper-scale experiment | NOT IMPLEMENTED | No 10,000-sample experiment was run. |

The project must be described as paper-inspired unless the exact retriever, decomposition procedure, aggregation rule, baselines, and experimental protocol are implemented and validated.
