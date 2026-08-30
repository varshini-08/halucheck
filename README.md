# HaluCheck
HaluCheck is an explainable hallucination-detection project. It preserves an LLM response, decomposes it into atomic facts, retrieves evidence from a local FAISS knowledge base with Wikipedia fallback, verifies facts with DeBERTa-v3 MNLI, and highlights the result in Streamlit.
## Architecture and project status
The project is organized into four implementation phases: response analysis, evidence retrieval, fact verification, and HaluEval evaluation. Detailed architecture, paper alignment, evaluation instructions, and the final status are documented in [docs/architecture.md](docs/architecture.md), [docs/paper_methodology.md](docs/paper_methodology.md), [docs/evaluation.md](docs/evaluation.md), and [docs/final_project_status.md](docs/final_project_status.md).

Additional release documentation: [ARCHITECTURE.md](ARCHITECTURE.md), [SOURCE_INTEGRATION.md](SOURCE_INTEGRATION.md), [VERIFICATION_METHODOLOGY.md](VERIFICATION_METHODOLOGY.md), [PERFORMANCE_BENCHMARK.md](PERFORMANCE_BENCHMARK.md), [TESTING.md](TESTING.md), [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md), and [FINAL_PROJECT_STATUS.md](FINAL_PROJECT_STATUS.md).
Demo materials: [DEMO_TEST_CASES.md](DEMO_TEST_CASES.md) and [DEMO_READINESS_SUMMARY.md](DEMO_READINESS_SUMMARY.md).
Submission materials: [FINAL_DEMO_SCRIPT.md](FINAL_DEMO_SCRIPT.md) and [VIVA_QUESTIONS_AND_ANSWERS.md](VIVA_QUESTIONS_AND_ANSWERS.md).
Final validation materials: [FINAL_MANUAL_VALIDATION_REPORT.md](FINAL_MANUAL_VALIDATION_REPORT.md), [FINAL_SCREENSHOT_CHECKLIST.md](FINAL_SCREENSHOT_CHECKLIST.md), [FINAL_SUBMISSION_CHECKLIST.md](FINAL_SUBMISSION_CHECKLIST.md), and [FINAL_RELEASE_CHECKLIST.md](FINAL_RELEASE_CHECKLIST.md).
## Installation and configuration
```text
pip install -r requirements.txt
```
Create `.env` from `.env.example` and set `GROQ_API_KEY` for interactive response generation. Groq remains the default provider. Gemini is optional: set `LLM_PROVIDER=gemini`, `GEMINI_API_KEY`, and optionally `GEMINI_MODEL` only for explicit generation or the LLM-as-judge baseline. Never commit either key. HaluEval benchmarking does not require an LLM request because it verifies the responses supplied by the dataset.
Install the spaCy model and build the local index when setting up a fresh environment:
```text
python -m spacy download en_core_web_sm
python scripts/build_index.py
```
Run the application with `streamlit run app.py`.
## Phase 3: retrieval and verification (implemented)
The existing pipeline extracts atomic facts, retrieves local FAISS evidence with Wikipedia fallback, and verifies each fact with DeBERTa-v3-MNLI. The Streamlit dashboard remains the interactive demonstration.
## Phase 4: HaluEval evaluation and benchmarking
Evaluation is isolated in `evaluation/` and reuses `services.analysis_service.HaluCheckPipeline.analyse` and `verification.verification_pipeline.VerificationPipeline.verify_many`. Place HaluEval `general_data.json` under `data/halu_eval/` (or provide another path). Records must contain `user_query`, `llm_response`, and a hallucination label (boolean, 0/1, or supported string label).
Run a reproducible benchmark on the supplied HaluEval responses:
`python -m evaluation.benchmark_runner --dataset data/halu_eval/general_data.json --samples 10 --seed 42`
By default, results are written to `results/halueval_10/` as `predictions.json`, `predictions.csv`, `metrics.json`, `report.json`, and `evaluation_report.json`. Each prediction records the supplied sample response, fact counts, confidence, latency, retrieval configuration, NLI model, and any error. The report computes accuracy, precision, recall, F1, TP/TN/FP/FN, confusion matrix, failed samples, and average latency. Use `--samples 50` or `--samples 100` for later development runs; avoid the full dataset initially.
The benchmark verifies the `llm_response` already present in HaluEval. It does not call Groq or generate a replacement response. The current 10-sample run evaluated 10 samples with 0 failures; its generated metrics are in `results/halueval_10/metrics.json`.
## Setup
`pip install -r requirements.txt`
Set `GROQ_API_KEY` in `.env`, install `en_core_web_sm`, build the index with `python scripts/build_index.py`, then run `streamlit run app.py`.
Phase 4 outputs are generated programmatically; no metric values are hard-coded. API keys are never included in logs or reports.
## Retrieval performance
Wikipedia remains a fallback after local FAISS retrieval. Wikipedia queries are normalized and cached, article chunk rankings are cached per article/fact, and duplicate batch facts are skipped. Retrieval timing is exposed through `EvidenceRetriever.last_timings` and `WikipediaService.last_timings`, including local FAISS, Wikipedia search, article retrieval, chunk ranking, and total evidence retrieval.
The measured repeatable sample check used HaluEval sample `1964`: the saved pre-optimization hybrid run took 56.71 seconds and the optimized run took 28.99 seconds (48.87% lower end-to-end time). The NLI result remained `NEUTRAL` with confidence 0.6592. This is one observed run, not a universal speed guarantee; model loading, network state, and cache state affect wall-clock timing.
## Paper evaluation artifacts
The isolated research modules are documented in `paper_alignment_report.md`, `paper_methodology.md`, `evaluation.md`, and `FINAL_COMPLETION_REPORT.md`. Build the optional GTR index with `python scripts/build_index.py --retrieval-mode paper`; it never replaces the MiniLM production index. Generate measured timing artifacts with `python -m evaluation.generate_performance --predictions results/halueval_100/predictions.json`. SelfCheckNLI is explicitly unavailable for the one-response general dataset unless additional responses are supplied. Paper decomposition and aggregation are marked PARTIAL MATCH where the publication does not specify exact implementation details.
GTR paper mode uses `sentence-transformers/gtr-t5-base`, has an explicit 768-dimensional offline smoke test, and uses the isolated `vector_db/gtr_base.index` plus matching metadata/manifest. It has completed the preserved 10-sample experiment (10/10 successful; accuracy 0.70; TP 0, TN 7, FP 1, FN 2). It never replaces the `all-MiniLM-L6-v2` production index. Rebuild it, when needed, with `python scripts/build_index.py --retrieval-mode paper`.

Test Gemini configuration without printing credentials:
`python scripts/test_gemini.py`

Run the optional Gemini judge on a small sample (requires `GEMINI_API_KEY`):
`python -m evaluation.baseline_runner --baseline llm --provider gemini --dataset data/halu_eval/general_data.json --samples 2 --seed 42`
## Performance profiling

Use:

`python -m evaluation.profile_pipeline --dataset data/halu_eval/general_data.json --sample-index 0`

This profiles the existing pipeline without generating a new Groq response. Uninstrumented stage values remain null rather than estimated.

## Final validated status

- Production retrieval: `all-MiniLM-L6-v2` (384 dimensions), using `vector_db/vector.index`.
- Paper retrieval: `sentence-transformers/gtr-t5-base` (768 dimensions), using `vector_db/gtr_base.index`.
- NLI: `MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli`; validate local loading with `python scripts/test_nli_model.py --offline`.
- HaluEval artifacts: 10-sample accuracy 0.70; 50-sample accuracy 0.80; 100-sample result has 99 valid records and accuracy 0.8081 over those records.
- Tests: `python -m pytest -q tests`; run Streamlit with `python -m streamlit run app.py`.

Results are under `results/`. See `FINAL_MASTER_STATUS.md` for the authoritative submission status. Gemini's 10-sample baseline remains incomplete due to quota, SelfCheckNLI requires legitimate multi-response data, browser interaction/screenshots remain manual work, cost analysis is not verified, and paper alignment is partial/paper-inspired rather than an exact reproduction.

For a complete Windows PowerShell walkthrough of the existing checkout, see [docs/MANUAL_LOCAL_EXECUTION_GUIDE.md](docs/MANUAL_LOCAL_EXECUTION_GUIDE.md) and [FINAL_LOCAL_EXECUTION_REPORT.md](FINAL_LOCAL_EXECUTION_REPORT.md).

## Multi-source source registry

The API exposes `GET /api/sources` and `GET /api/sources/status` so the React
frontend can display truthful source capabilities. Local FAISS and Wikipedia
remain the active retrieval adapters; optional sources are documented in
[SOURCE_INTEGRATION_REPORT.md](SOURCE_INTEGRATION_REPORT.md) and their empty
credentials are listed in `.env.example`. Never place API keys in React code.
The release-level audit is [FINAL_RELEASE_AUDIT.md](FINAL_RELEASE_AUDIT.md); it separates validated results from manual or external-resource limitations.
