# HaluCheck Final Project Status

## Scope completed

- Phase 1 response analysis: Groq response generation, spaCy sentence processing, atomic facts, entities, and entity matching.
- Phase 2 evidence: local JSON knowledge base, SentenceTransformer embeddings, persistent FAISS index, local-first retrieval, Wikipedia fallback, normalized query/article/ranking caches, duplicate elimination, timeout handling, and retrieval timings.
- Phase 3 verification: DeBERTa-v3 MNLI, supported/contradicted/neutral labels, fact-level aggregation, hallucination decision, and Streamlit highlighting.
- Phase 4 evaluation: HaluEval loader, supplied-response benchmark, reproducible sampling, metrics, confusion matrices, JSON/CSV reports, and three-way comparative evaluation.
- Final stabilization: methodology comparison, architecture documentation, evaluation documentation, dashboard factuality/evidence/mode/timing summary, and full regression validation.
- Optional paper retrieval backend: `RETRIEVAL_MODE=paper` selects GTR-Base with separate index paths; preflight currently reports unavailable because the model/index are not cached.

## Paper alignment

The repository follows the paper's broad flow: response, atomic facts, dense retrieval, top evidence, NLI, thresholded fact decision, and visual explanation. It is not an exact reproduction. The atomic decomposition is a spaCy rule-based implementation rather than the paper's InstructGPT-style 8-shot process. Retrieval uses all-MiniLM-L6-v2 rather than GTR-Base, and the NLI aggregation uses fact-level strong-evidence rules rather than the paper's exact average-entailment formulation. Paper-specific SelfCheckNLI, prompt-based GPT baselines, and cost analysis are not implemented.

See [paper_methodology.md](paper_methodology.md) for the component-by-component status.

## Models and data

- Response model: Groq `openai/gpt-oss-20b`.
- Embeddings: `sentence-transformers/all-MiniLM-L6-v2`.
- NLI: `MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli`.
- Dataset: `data/halu_eval/general_data.json` and smoke data.
- Local corpus: `knowledge_base/wikipedia.json`.
- Index: `vector_db/vector.index` and metadata.

## Recorded evaluation

The existing 10-sample comparison used seed 42 and identical sample IDs:

| Configuration | Accuracy | Precision | Recall | F1 | Average latency |
|---|---:|---:|---:|---:|---:|
| NLI-only | 70% | 0% | 0% | 0% | 9.36s |
| Local KB | 80% | 50% | 50% | 50% | 8.19s |
| Hybrid | 80% | 0% | 0% | 0% | 92.87s |

These are development results from 10 samples, not paper-level claims.

## Performance validation

For HaluEval sample `1964`, the saved pre-optimization hybrid run took 56.71 seconds and the optimized rerun took 28.99 seconds, an observed 48.87% lower end-to-end time. The NLI output stayed `NEUTRAL` at confidence 0.6592. The result is a single controlled observation and is affected by model, network, and cache state.

## Validation status

The final test run completed with `55 passed, 1 skipped` and three existing dependency deprecation warnings. Syntax and diagnostics checks passed for the changed modules. No API keys were written to benchmark artifacts or documentation. The Streamlit health endpoint returned `200 ok`, the configured Groq model was confirmed available to the account, FAISS was synchronized at 7 vectors/384 dimensions, and real DeBERTa controlled checks returned supported/contradicted/neutral as expected.

The post-fix 10-sample benchmark evaluated 10 samples with 0 failures: accuracy 70%, precision 0%, recall 0%, and F1 0%, with TP=0, TN=7, FP=1, FN=2 and average latency 105.17 seconds/sample. The 50-sample result in `results/halueval_50/` was generated before the numbered-list fix and should be treated as a pre-fix reference. The 100-sample run was started but stopped at approximately sample 25 because it became resource-heavy; no final 100-sample artifact exists and no 100-sample metric is claimed.

The stabilized comparative run used the same 10 sample IDs across all three configurations. Local KB reached 80% accuracy, hybrid reached 80%, and NLI-only reached 70%. Hybrid had the same accuracy as local KB but much higher observed latency on this split.

The optional GTR paper preflight was executed and reported `sentence-transformers/gtr-t5-base` with separate index paths as unavailable because no checkpoint or index is cached. No GTR metrics are claimed. SelfCheckNLI, GPT baseline, and cost pricing remain unavailable because their exact paper protocols/pricing are not implemented or verified.

## Remaining work

- Verify the exact paper checkpoint, top-K, threshold, preprocessing, and 10,000-sample protocol from the authoritative publication if exact reproduction is required.
- Implement paper baselines such as SelfCheckNLI and prompt-based GPT evaluation if comparative paper replication is required.
- Add provider cost accounting if cost comparisons are required.
- Run larger 50/100-sample experiments only after confirming runtime and network budget.
- Build and benchmark the optional GTR index only if exact paper retrieval comparison is required: `python scripts/build_index.py --retrieval-mode paper`.
- Launch Streamlit manually for a browser-level visual acceptance check; import and dashboard renderer tests pass.

## Final command

```text
streamlit run app.py
```

For evaluation:

```text
python -m evaluation.benchmark_runner --dataset data/halu_eval/general_data.json --samples 10 --seed 42
python -m evaluation.comparative_runner --dataset data/halu_eval/general_data.json --samples 10 --seed 42
```
