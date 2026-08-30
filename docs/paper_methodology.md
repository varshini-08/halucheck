# HaluCheck Paper Methodology Comparison

This comparison is based on the supplied description of the 2025 HaluCheck paper and the implementation in this repository. It intentionally distinguishes exact matches from component substitutions.

| Component | Paper methodology | Current implementation | Status |
|---|---|---|---|
| Input | User query and an LLM response | Streamlit accepts a query and Groq generates a response; HaluEval uses its supplied `llm_response` | MATCH |
| Atomic decomposition | InstructGPT-style 8-shot atomic-fact decomposition | spaCy-based sentence/dependency rules with coordination, list, date, duplicate, and completeness handling | DIFFERENT |
| Dense retriever | GTR-Base, described as 768-dimensional embeddings | `sentence-transformers/all-MiniLM-L6-v2` with FAISS | DIFFERENT |
| Evidence source | Wikipedia corpus | Local Wikipedia-style JSON knowledge base plus live Wikipedia API fallback | PARTIAL MATCH |
| Retrieval index | FAISS top-K dense retrieval | FAISS inner-product search over normalized embeddings | PARTIAL MATCH |
| Top-K | Paper-specific top-K setting | Default top-K is 3; Wikipedia is capped by `MAX_WIKIPEDIA_CHUNKS` | PARTIAL MATCH |
| Evidence selection | Retrieved documents/passages used for NLI | Local evidence or ranked Wikipedia article chunks are passed to NLI | PARTIAL MATCH |
| NLI | NLI entailment scoring | DeBERTa-v3 MNLI-FEVER-ANLI with supported, contradicted, and neutral probabilities | PARTIAL MATCH |
| Aggregation | Average entailment score and threshold | Fact classifier selects strong supported/contradicted evidence using a 0.70 confidence threshold; strongest contradiction can override support | DIFFERENT |
| Hallucination rule | Thresholded average entailment | Any contradicted fact is a hallucination; neutral is uncertain and is not automatically hallucinated | DIFFERENT |
| Confidence | Paper-specific entailment confidence/threshold | Mean fact-classification confidence in benchmark reports and mean NLI confidence in the dashboard | DIFFERENT |
| Visualization | Highlight hallucinated sentences | Original response is preserved and highlighted green, red, or orange by fact label | PARTIAL MATCH |
| Dataset | HaluEval QA evaluation, paper reports a large sampled experiment | HaluEval JSON/JSONL loader with reproducible 10/50/100-sample CLI runs | PARTIAL MATCH |
| Baselines | Paper comparisons include SelfCheckNLI and prompt-based GPT evaluation | NLI-only, local KB, and hybrid HaluCheck configurations are implemented; paper baselines are not implemented | DIFFERENT |
| Metrics | Accuracy, precision, recall, F1, latency, and cost | Accuracy, precision, recall, F1, TP/TN/FP/FN, confusion matrix, latency, and failure counts | PARTIAL MATCH |
| Cost | Paper-level cost analysis | No provider cost accounting is implemented | NOT IMPLEMENTED |

## Current decision rule

For each retrieved evidence item, DeBERTa returns `SUPPORTED`, `CONTRADICTED`, or `NEUTRAL`. A fact is marked hallucinated only when a strong contradiction is selected by `FactClassifier`. Supported facts are factual, contradicted facts are hallucinated, and neutral facts are uncertain/unverified. The response-level benchmark label is `hallucination` when any fact is marked hallucinated; otherwise it is `no_hallucination`.

## Paper-compatible mode decision

The current all-MiniLM-L6-v2 mode remains the default because its index is present and tested. Optional `RETRIEVAL_MODE=paper` selects `sentence-transformers/gtr-t5-base` and separate `vector_db/gtr_base.index`/`vector_db/gtr_base_metadata.pkl` artifacts. The paper preflight currently reports this mode as unavailable because no GTR checkpoint or separate index is cached. Build it explicitly with `python scripts/build_index.py --retrieval-mode paper`; this may download a large model and is intentionally not performed automatically. The current system should therefore be described as paper-inspired, not an exact reproduction.
