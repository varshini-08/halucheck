from __future__ import annotations

import argparse
import csv
import json
import logging
import random
import time
from pathlib import Path

from services.analysis_service import HaluCheckPipeline
from verification.verification_pipeline import VerificationPipeline
from .halu_eval_loader import load_halueval
from .benchmark_adapter import adapt
from .metrics import calculate_metrics
from .generate_report import write_report

LOGGER = logging.getLogger(__name__)
RETRIEVAL_CONFIGURATION = "hybrid local knowledge base + Wikipedia fallback"
NLI_MODEL = "MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli"
PREDICTED_LABELS = {"hallucination", "no_hallucination"}


def _output_directory(results_dir, limit: int) -> Path:
    return Path(results_dir) if results_dir is not None else Path("results") / f"halueval_{limit}"


def _classification_counts(classifications):
    return {
        "fact_count": len(classifications),
        "supported_fact_count": sum(item.label == "SUPPORTED" for item in classifications),
        "contradicted_fact_count": sum(item.label == "CONTRADICTED" for item in classifications),
        "neutral_fact_count": sum(item.label == "NEUTRAL" for item in classifications),
    }


def _average_confidence(classifications) -> float:
    return sum(item.confidence for item in classifications) / len(classifications) if classifications else 0.0


def run_benchmark(dataset_path, limit=50, seed=42, pipeline=None, results_dir=None):
    if limit < 1:
        raise ValueError("samples must be at least 1")

    samples = list(load_halueval(str(dataset_path)))
    random.Random(seed).shuffle(samples)
    samples = samples[:limit]
    pipeline = pipeline or HaluCheckPipeline(verification_pipeline=VerificationPipeline())
    rows = []
    for index, sample in enumerate(samples, 1):
        item = adapt(sample)
        started = time.perf_counter()
        error = None
        classifications = []
        try:
            # HaluEval supplies the response; only that response is verified.
            result=pipeline.analyse(item.response, question=item.question)
            classifications=result.verifications
            hallucinated=any(c.hallucination for c in classifications)
            predicted="hallucination" if hallucinated else "no_hallucination"
            confidence=_average_confidence(classifications)
            verification=[{"fact":c.fact,"label":c.label,"confidence":c.confidence,"reason":c.reason} for c in classifications]
        except Exception as exc:
            LOGGER.error("Sample %s failed during verification", item.sample_id)
            predicted="error"
            confidence=0.0
            verification=[]
            error=str(exc)
        counts = _classification_counts(classifications)
        rows.append({"sample_id":item.sample_id,"query":item.question,"response":item.response,"expected_label":item.expected_label,"predicted_label":predicted,**counts,"confidence":confidence,"processing_time_seconds":time.perf_counter()-started,"retrieval_configuration":RETRIEVAL_CONFIGURATION,"nli_model":NLI_MODEL,"verification":verification,"error":error})
        LOGGER.info("Processed %d/%d", index, len(samples))

    out = _output_directory(results_dir, limit)
    out.mkdir(parents=True, exist_ok=True)
    (out / "predictions.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    csv_fields = ["sample_id", "query", "response", "expected_label", "predicted_label", "fact_count", "supported_fact_count", "contradicted_fact_count", "neutral_fact_count", "confidence", "processing_time_seconds", "retrieval_configuration", "nli_model", "error"]
    with (out / "predictions.csv").open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=csv_fields)
        writer.writeheader()
        writer.writerows({key: row[key] for key in csv_fields} for row in rows)

    valid = [row for row in rows if row["predicted_label"] in PREDICTED_LABELS]
    metrics = calculate_metrics([row["expected_label"] for row in valid], [row["predicted_label"] for row in valid])
    metrics["evaluated_samples"] = len(rows)
    metrics["failed_samples"] = len(rows) - len(valid)
    metrics["average_processing_time_seconds"] = sum(row["processing_time_seconds"] for row in rows) / len(rows) if rows else 0.0
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    report = write_report(metrics, out / "report.json", dataset_path, len(rows), metrics["average_processing_time_seconds"], RETRIEVAL_CONFIGURATION, NLI_MODEL)
    write_report(metrics, out / "evaluation_report.json", dataset_path, len(rows), metrics["average_processing_time_seconds"], RETRIEVAL_CONFIGURATION, NLI_MODEL)
    print_summary(report)
    return metrics, rows


def print_summary(report):
    metrics = report["metrics"]
    print(f"HaluEval benchmark: {report['evaluated_samples']} samples")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall: {metrics['recall']:.4f}")
    print(f"F1: {metrics['f1_score']:.4f}")
    print(f"TP: {metrics['tp']} | TN: {metrics['tn']} | FP: {metrics['fp']} | FN: {metrics['fn']}")
    print(f"Average latency: {report['average_processing_time_seconds']:.4f}s")
    print(f"Failed samples: {metrics['failed_samples']}")


def main():
    ap = argparse.ArgumentParser(description="Run HaluEval benchmark through HaluCheck")
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--samples", type=int, default=50)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--results-dir", default=None)
    ap.add_argument("--log-level", default="INFO")
    args = ap.parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO), format="%(levelname)s %(message)s")
    run_benchmark(args.dataset, args.samples, args.seed, results_dir=args.results_dir)


if __name__ == "__main__": main()

def compare_configurations(dataset_path, pipelines, limit=50, seed=42, results_dir="results"):
    """Evaluate identical sampled records with named caller-supplied Phase 3 pipelines."""
    table = {}
    for name, configured_pipeline in pipelines.items():
        metrics, _ = run_benchmark(dataset_path, limit, seed, pipeline=configured_pipeline, results_dir=Path(results_dir) / name)
        table[name] = {key: metrics[key] for key in ("accuracy", "precision", "recall", "f1_score")}
    Path(results_dir).mkdir(parents=True, exist_ok=True)
    (Path(results_dir) / "comparison.json").write_text(json.dumps(table, indent=2), encoding="utf-8")
    return table









