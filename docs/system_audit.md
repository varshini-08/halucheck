# HaluCheck System Audit

## Architecture verification

The active Streamlit path is `app.py` -> `LLMService.generate_response` -> `HaluCheckPipeline.analyse` -> `AtomicFactExtractor`/`EntityMatcher` -> `EvidenceRetriever` -> `VerificationPipeline` -> `FactClassifier`/`NLIVerifier` -> `visualization.dashboard.render_analysis`.

HaluEval bypasses Groq as required: `evaluation.benchmark_runner` passes each supplied `llm_response` directly to `HaluCheckPipeline.analyse`. Comparative evaluation reuses the same sampled records for NLI-only, local-KB, and hybrid configurations.

## Component inventory

| Component | Location | Actual implementation | Tested |
|---|---|---|---|
| LLM generation | `services/llm_service.py` | Groq SDK, configurable model | Yes, mocked |
| Atomic facts | `extraction/atomic_fact_extractor.py` | spaCy dependency/rule-based decomposition | Yes |
| Entities | `extraction/entity_detection.py` | spaCy named entities | Yes |
| Entity matching | `verification/entity_matcher.py` | RapidFuzz plus strict labels | Yes |
| Local evidence | `services/vector_store.py`, `knowledge_base/` | normalized SentenceTransformer vectors and FAISS | Yes |
| Wikipedia | `services/wikipedia_service.py` | MediaWiki search/extract API, cache, ranking | Yes with fake API |
| Retrieval policy | `services/retriever.py` | local-first, thresholded Wikipedia fallback | Yes |
| NLI | `verification/nli_verifier.py` | cached DeBERTa-v3 MNLI-FEVER-ANLI | Yes with fake verifier; real model exercised |
| Fact classification | `verification/fact_classifier.py` | strong support/contradiction threshold 0.70 | Yes |
| Dashboard | `app.py`, `visualization/dashboard.py` | Streamlit response highlighting and summaries | Import/render tests |
| HaluEval | `evaluation/` | JSON/JSONL loader, benchmark and comparative CLI | Yes |

## Security

`.env` is ignored, benchmark outputs contain no API-key values, and logs mask no secrets because key values are never logged. FAISS metadata uses pickle; this is a trusted local artifact and must not be loaded from untrusted input.

## Findings

The audit found and fixed numbered-list and Markdown-table extraction defects: spaCy could merge list lines or table presentation rows into malformed source sentences. Multi-line numbered/bulleted responses and Markdown tables are now handled at the source-unit boundary, with regression tests. The completed post-fix suite has 55 passing tests. The optional GTR paper profile and preflight are implemented, but its model/index are not cached. Known limitations are documented in `paper_methodology.md` and `final_project_status.md`: the implementation is paper-inspired rather than paper-exact, and manual browser interaction coverage remains limited.
