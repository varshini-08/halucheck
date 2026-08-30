"""Run comparable HaluEval experiments over one shared sample."""

from __future__ import annotations

import argparse
import csv
import json
import logging
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

from extraction.atomic_fact_extractor import AtomicFactExtractor
from services.analysis_service import AnalysisResult, HaluCheckPipeline
from services.retriever import EvidenceRetriever, FactRetrieval
from services.vector_store import Evidence
from verification.verification_pipeline import VerificationPipeline

from .benchmark_adapter import adapt
from .benchmark_runner import NLI_MODEL, RETRIEVAL_CONFIGURATION
from .halu_eval_loader import HaluEvalSample, load_halueval
from .metrics import calculate_metrics

LOGGER = logging.getLogger(__name__)
CONFIGURATIONS = ("nli_only", "local_kb", "hybrid")


@dataclass(frozen=True)
class Configuration:
    name: str
    description: str
    factory: Callable[[], object]


class NLIOnlyPipeline:
    """Use the supplied response as NLI premise without external retrieval."""

    def __init__(self) -> None:
        self.extractor = AtomicFactExtractor()
        self.verification = VerificationPipeline()

    def analyse(self, response: str, question: str = "") -> AnalysisResult:
        facts = self.extractor.extract_atomic_facts(response)
        retrievals = [
            FactRetrieval(
                fact.fact_text,
                [Evidence("HaluEval response", response, 1.0, 1, "response")],
            )
            for fact in facts
        ]
        verifications = self.verification.verify_many(retrievals)
        return AnalysisResult(response, facts, {"total_facts": len(facts)}, retrievals, verifications)


def _configurations() -> tuple[Configuration, ...]:
    return (
        Configuration("nli_only", "NLI using the supplied response as premise", NLIOnlyPipeline),
        Configuration(
            "local_kb",
            "NLI with local FAISS knowledge-base evidence only",
            lambda: HaluCheckPipeline(
                retriever=EvidenceRetriever(enable_wikipedia_fallback=False),
                verification_pipeline=VerificationPipeline(),
            ),
        ),
        Configuration(
            "hybrid",
            RETRIEVAL_CONFIGURATION,
            lambda: HaluCheckPipeline(verification_pipeline=VerificationPipeline()),
        ),
    )


def _classification_summary(result: AnalysisResult) -> tuple[dict, list[dict]]:
    classifications = result.verifications
    predicted = "hallucination" if any(item.hallucination for item in classifications) else "no_hallucination"
    verification = [
        {
            "fact": item.fact,
            "label": item.label,
            "confidence": item.confidence,
            "hallucination": item.hallucination,
            "reason": item.reason,
        }
        for item in classifications
    ]
    counts = {
        "fact_count": len(classifications),
        "supported_fact_count": sum(item.label == "SUPPORTED" for item in classifications),
        "contradicted_fact_count": sum(item.label == "CONTRADICTED" for item in classifications),
        "neutral_fact_count": sum(item.label == "NEUTRAL" for item in classifications),
    }
    confidence = sum(item.confidence for item in classifications) / len(classifications) if classifications else 0.0
    return {"predicted_label": predicted, **counts, "confidence": confidence}, verification


def _run_configuration(samples: Iterable[HaluEvalSample], configuration: Configuration) -> tuple[dict, list[dict]]:
    pipeline = configuration.factory()
    rows = []
    for index, sample in enumerate(samples, 1):
        item = adapt(sample)
        started = time.perf_counter()
        error = None
        details = {"predicted_label": "error", "fact_count": 0, "supported_fact_count": 0, "contradicted_fact_count": 0, "neutral_fact_count": 0, "confidence": 0.0}
        verification = []
        try:
            result = pipeline.analyse(item.response, question=item.question)
            details, verification = _classification_summary(result)
        except Exception as exc:
            error = str(exc)
            LOGGER.error("Configuration %s failed for sample %s: %s", configuration.name, item.sample_id, error)
        rows.append({
            "sample_id": item.sample_id,
            "query": item.question,
            "response": item.response,
            "expected_label": item.expected_label,
            **details,
            "processing_time_seconds": time.perf_counter() - started,
            "configuration": configuration.name,
            "configuration_description": configuration.description,
            "nli_model": NLI_MODEL,
            "verification": verification,
            "error": error,
        })
        LOGGER.info("[%s] processed %d samples", configuration.name, index)

    valid = [row for row in rows if row["predicted_label"] in {"hallucination", "no_hallucination"}]
    metrics = calculate_metrics(
        [row["expected_label"] for row in valid],
        [row["predicted_label"] for row in valid],
    )
    metrics["evaluated_samples"] = len(rows)
    metrics["failed_samples"] = len(rows) - len(valid)
    metrics["average_processing_time_seconds"] = sum(row["processing_time_seconds"] for row in rows) / len(rows) if rows else 0.0
    return metrics, rows


def _write_configuration_outputs(directory: Path, metrics: dict, rows: list[dict]) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "predictions.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    fields = ["sample_id", "query", "response", "expected_label", "predicted_label", "fact_count", "supported_fact_count", "contradicted_fact_count", "neutral_fact_count", "confidence", "processing_time_seconds", "configuration", "configuration_description", "nli_model", "error"]
    with (directory / "predictions.csv").open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row[field] for field in fields} for row in rows)
    (directory / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (directory / "report.json").write_text(json.dumps({"metrics": metrics, "nli_model": NLI_MODEL}, indent=2), encoding="utf-8")


def run_comparison(dataset_path, limit: int = 10, seed: int = 42, results_dir: str | Path = "results/halueval_comparison") -> dict:
    if limit < 1:
        raise ValueError("samples must be at least 1")
    samples = list(load_halueval(str(dataset_path)))
    random.Random(seed).shuffle(samples)
    samples = samples[:limit]
    output = Path(results_dir)
    results = {}
    sample_ids = [sample.sample_id for sample in samples]

    for configuration in _configurations():
        metrics, rows = _run_configuration(samples, configuration)
        _write_configuration_outputs(output / configuration.name, metrics, rows)
        results[configuration.name] = {"metrics": metrics, "sample_ids": [row["sample_id"] for row in rows]}

    comparison_rows = []
    for name in CONFIGURATIONS:
        metrics = results[name]["metrics"]
        comparison_rows.append({
            "configuration": name,
            "accuracy": metrics["accuracy"],
            "precision": metrics["precision"],
            "recall": metrics["recall"],
            "f1_score": metrics["f1_score"],
            "average_processing_time_seconds": metrics["average_processing_time_seconds"],
        })
    output.mkdir(parents=True, exist_ok=True)
    comparison = {"dataset": str(dataset_path), "samples": len(samples), "seed": seed, "sample_ids": sample_ids, "configurations": results, "table": comparison_rows}
    (output / "comparison.json").write_text(json.dumps(comparison, indent=2), encoding="utf-8")
    with (output / "comparison.csv").open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(comparison_rows[0]))
        writer.writeheader()
        writer.writerows(comparison_rows)
    (output / "comparison_report.json").write_text(json.dumps({"dataset": str(dataset_path), "samples": len(samples), "seed": seed, "sample_ids": sample_ids, "table": comparison_rows}, indent=2), encoding="utf-8")
    lines = ["# Comparative Evaluation", "", "| Configuration | Accuracy | Precision | Recall | F1 | Avg Latency |", "|---|---:|---:|---:|---:|---:|"]
    lines.extend(
        f"| {row['configuration']} | {row['accuracy']:.4f} | {row['precision']:.4f} | {row['recall']:.4f} | {row['f1_score']:.4f} | {row['average_processing_time_seconds']:.4f}s |"
        for row in comparison_rows
    )
    (output / "comparison.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Configuration | Accuracy | Precision | Recall | F1 | Avg Latency")
    for row in comparison_rows:
        print(f"{row['configuration']} | {row['accuracy']:.4f} | {row['precision']:.4f} | {row['recall']:.4f} | {row['f1_score']:.4f} | {row['average_processing_time_seconds']:.4f}s")
    return comparison


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare HaluCheck verification configurations on HaluEval")
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--samples", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--results-dir", default="results/halueval_comparison")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    run_comparison(args.dataset, args.samples, args.seed, args.results_dir)


if __name__ == "__main__":
    main()
