# Final Experimental Results

> **Current GTR result (2026-08-28; supersedes stale blocked statements below):** local GTR, isolated 768d index, and 3-query offline smoke PASS. GTR HaluEval 2 completed 2/2 (accuracy 1.00, TN 2); GTR HaluEval 10 completed 10/10 with 0 failures: accuracy 0.70, precision/recall/F1 0.00, TP 0, TN 7, FP 1, FN 2. Recalculation from raw predictions matches `metrics.json`. Average processing was 8.8605 s; GTR retrieval 1.4069 s; NLI inference 7.0538 s. GTR 50/100 was not run.

This document records only experiments with evidence in this repository. No
metrics are manually entered and unavailable experiments are not presented as
completed.

## Environment and dataset

- Dataset: `data/halu_eval/general_data.json` (4,507 records)
- Seed used by benchmark runs: 42
- Production embedding model: `sentence-transformers/all-MiniLM-L6-v2`
- NLI model: DeBERTa-v3-MNLI
- Optional paper retrieval model: `sentence-transformers/gtr-t5-base`

## Validated results

| Experiment | Accuracy | Precision | Recall | F1 | Evidence |
|---|---:|---:|---:|---:|---|
| HaluEval 10 | 70% | 0% | 0% | 0% | `results/halueval_10/metrics.json` |
| HaluEval 50 | 80% | 25% | 12.5% | 16.67% | `results/halueval_50/metrics.json` |
| HaluEval 100 (seed 42) | 80.81%* | 0% | 0% | 0% | `results/halueval_100/metrics.json` |

The comparative MiniLM experiments are recorded in
`results/halueval_comparison/`.

\* 100 samples were attempted; 99 produced predictions and 1 failed. The
metrics are calculated over the 99 valid predictions, while the output records
`evaluated_samples: 100` and `failed_samples: 1`.

## Performance validation

The measured cold/warm validation is in
`results/performance/final_validation.json`: cold 16.89 seconds, warm 1.03
seconds, with identical predictions and one retrieval-cache hit on the warm
pass. Uninstrumented production stages are reported as `null`, never estimated.

## Status of remaining experiments

- 100-sample benchmark: **COMPLETE**. Seed 42, 100 attempted, 99 successful,
  1 failed; accuracy 0.8081, TN 80, FN 19, FP 0, TP 0, average latency 8.7346
  seconds over valid samples.
- GTR: **BLOCKED at runtime**. The separate 768-dimensional index and manifest
  exist. The model is now verified locally and the offline 10-sample run
  completed: accuracy 0.80, precision 0, recall 0, F1 0, TN 8, FN 2, with no
  failed samples. Results are in `results/halueval_gtr_10/`. GTR retrieval
  itself used no network; the existing NLI verifier may still attempt its own
  model fetch when its cache is incomplete.
- LLM-as-judge: **NOT EXECUTED** unless `GROQ_API_KEY` is configured; the
  adapter never prints or stores credentials.
- SelfCheckNLI: **NOT REPRODUCIBLE from available data** because
  `general_data.json` contains one response per prompt. See
  `results/baselines/selfchecknli/status.md`.
- Browser validation: manual-only and not claimed as executed here.
- Exact paper decomposition and aggregation: **PARTIAL MATCH** because the
  published implementation details are underspecified; see
  `docs/final_paper_alignment.md`.
- Cost analysis: **NOT VERIFIED** without authoritative provider pricing.

## Reproduction commands

```powershell
python -m evaluation.benchmark_runner --dataset data/halu_eval/general_data.json --samples 100 --seed 42
python scripts/test_gtr.py
python scripts/build_index.py --retrieval-mode paper
python -m evaluation.paper_comparison --run-gtr --dataset data/halu_eval/general_data.json --samples 10 --seed 42
python -m evaluation.baseline_runner --baseline llm --dataset data/halu_eval/general_data.json --samples 10 --seed 42
python -m pytest -q
```

Current automated test evidence: **62 passed, 1 skipped, 3 warnings**.

## GTR validation update — 2026-08-28

| Experiment | Status | Result |
|---|---|---|
| GTR local model | PASS | Offline load, 768 dimensions |
| GTR index and manifest | PASS | 7 FAISS vectors / 7 metadata records |
| GTR offline smoke | PASS | 3/3 retrieval queries; no MiniLM or Wikipedia fallback |
| GTR HaluEval 2 | FAIL / BLOCKED | 2 attempted, 0 successful, 2 NLI-cache failures; no predictions or metrics claimed |
| GTR HaluEval 10 | NOT RUN | Gated on the 2-sample run |
| GTR vs MiniLM | NOT RUN | Requires valid GTR prediction records |

The prior text describing a completed offline 10-sample GTR result is not current validation evidence and must not be treated as a result of this run. Full details: `results/final_validation/GTR_VALIDATION_REPORT.md`.
