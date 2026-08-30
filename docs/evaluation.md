# Evaluation Guide

## Dataset

Place HaluEval data at `data/halu_eval/general_data.json`. The loader accepts JSON arrays, JSONL, and wrapper objects. Each sample must provide a question, response, and hallucination label. The benchmark evaluates the supplied `llm_response`; it never calls Groq to regenerate a response.

## Single configuration

Run the existing hybrid pipeline with a reproducible sample:

```text
python -m evaluation.benchmark_runner --dataset data/halu_eval/general_data.json --samples 10 --seed 42
python -m evaluation.benchmark_runner --dataset data/halu_eval/general_data.json --samples 50 --seed 42
python -m evaluation.benchmark_runner --dataset data/halu_eval/general_data.json --samples 100 --seed 42
```

Default output is `results/halueval_<sample_count>/` with predictions, CSV, metrics, and reports.

## Comparative experiment

The comparative runner uses exactly the same shuffled samples for all configurations:

```text
python -m evaluation.comparative_runner --dataset data/halu_eval/general_data.json --samples 10 --seed 42
```

It writes `results/halueval_comparison/` with `nli_only/`, `local_kb/`, `hybrid/`, `comparison.json`, `comparison.csv`, and `comparison_report.json`.

- `nli_only`: verifies the supplied response premise without external retrieval.
- `local_kb`: uses the existing FAISS knowledge base and disables Wikipedia fallback.
- `hybrid`: uses the existing local-first retrieval and Wikipedia fallback.

## Metrics

Metrics are calculated programmatically from valid predictions:

- Accuracy
- Precision
- Recall
- F1 score
- True positives, true negatives, false positives, false negatives
- Confusion matrix
- Average processing latency
- Failed sample count

## Recorded sample fields

Each prediction stores sample ID, question, original response, expected and predicted labels, fact counts, confidence, processing time, configuration/model metadata, verification details, and an error field.

## Current recorded 10-sample comparison

The checked-in generated comparison used seed 42 and these results:

| Configuration | Accuracy | Precision | Recall | F1 | Average latency |
|---|---:|---:|---:|---:|---:|
| NLI-only | 70% | 0% | 0% | 0% | 9.36s |
| Local KB | 80% | 50% | 50% | 50% | 8.19s |
| Hybrid | 80% | 0% | 0% | 0% | 92.87s |

These are development results from 10 samples and should not be presented as paper-level generalization results.
