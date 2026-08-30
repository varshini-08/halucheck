"""Optional paper-compatible retrieval preflight and comparison entry point."""

from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path

from services.analysis_service import HaluCheckPipeline
from services.retriever import EvidenceRetriever, RetrievalError
from verification.fact_classifier import FactClassifier
from verification.nli_verifier import NLIVerifier
from verification.verification_pipeline import VerificationPipeline

from .benchmark_adapter import adapt
from .cost import summarize
from .halu_eval_loader import load_halueval
from .metrics import calculate_metrics

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def paper_preflight() -> dict[str, object]:
    """Report whether the optional GTR backend is locally runnable."""
    retriever = EvidenceRetriever(retrieval_mode="paper")
    index_path = retriever.store.index_path
    metadata_path = retriever.store.metadata_path
    manifest_path = PROJECT_ROOT / "vector_db" / "gtr_base_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else None
    model_cache = "not checked until embedding load"
    return {
        "retrieval_mode": "paper",
        "model": retriever.model_name,
        "index": str(index_path),
        "metadata": str(metadata_path),
        "manifest_path": str(manifest_path),
        "index_available": index_path.exists() and metadata_path.exists(),
        "manifest": manifest,
        "model_cache": model_cache,
        "status": "ready" if index_path.exists() and metadata_path.exists() and manifest and manifest.get("embedding_dimension") == 768 else "unavailable: build the separate paper index first",
        "cost": "Cost unavailable",
    }


def run_paper_preflight(output: str | Path = "results/paper_comparison") -> dict[str, object]:
    """Write a truthful prerequisite report without downloading GTR."""
    result = paper_preflight()
    destination = Path(output)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "preflight.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return result


def run_gtr_comparison(dataset_path, limit: int = 10, seed: int = 42, output: str | Path = "results/gtr_comparison", offline: bool = False) -> dict:
    """Run the GTR configuration when its separate artifacts are available."""
    preflight = paper_preflight()
    if not preflight["index_available"]:
        raise RuntimeError(str(preflight["status"]))
    samples = list(load_halueval(str(dataset_path)))
    import random
    random.Random(seed).shuffle(samples)
    selected_ids: set[str] = set()
    selected = []
    for sample in samples:
        sample_id = str(adapt(sample).sample_id)
        if sample_id not in selected_ids:
            selected_ids.add(sample_id)
            selected.append(sample)
        if len(selected) == limit:
            break
    samples = selected
    pipeline = HaluCheckPipeline(
        retriever=EvidenceRetriever(retrieval_mode="paper", offline=offline),
        verification_pipeline=VerificationPipeline(FactClassifier(NLIVerifier(offline=offline))),
    )
    rows = []
    for sample in samples:
        item = adapt(sample)
        started = time.perf_counter()
        error = None
        try:
            result = pipeline.analyse(item.response, question=item.question)
            stage_error = result.comparison.get("retrieval_error") or result.comparison.get("verification_error")
            if stage_error:
                raise RuntimeError(str(stage_error))
            predicted = "hallucination" if any(fact.hallucination for fact in result.verifications) else "no_hallucination"
            row = {"sample_id": item.sample_id, "query": item.question, "response": item.response, "expected_label": item.expected_label, "predicted_label": predicted, "fact_count": len(result.facts), "evidence_count": sum(len(retrieval.retrieved_evidence) for retrieval in result.retrievals), "error": None, "retrieval_mode": "paper/GTR", "timings": result.comparison.get("timings", {})}
        except Exception as exc:
            error = str(exc)
            row = {"sample_id": item.sample_id, "query": item.question, "response": item.response, "expected_label": item.expected_label, "predicted_label": "error", "fact_count": 0, "evidence_count": 0, "error": error, "retrieval_mode": "paper/GTR", "timings": {}}
        row["processing_time_seconds"] = time.perf_counter() - started
        row["retrieval_model"] = pipeline.retriever.model_name
        row["embedding_dimension"] = getattr(getattr(pipeline.retriever.store, "_index", None), "d", None)
        rows.append(row)
    valid = [row for row in rows if row["predicted_label"] in {"hallucination", "no_hallucination"}]
    metrics = calculate_metrics([row["expected_label"] for row in valid], [row["predicted_label"] for row in valid])
    successful_times = [row["processing_time_seconds"] for row in valid]
    retrieval_times = [row["timings"].get("retrieval_seconds") for row in valid if row["timings"].get("retrieval_seconds") is not None]
    nli_times = [row["timings"].get("nli_inference_seconds") for row in valid if row["timings"].get("nli_inference_seconds") is not None]
    metrics.update({"attempted_samples": len(rows), "successful_samples": len(valid), "failed_samples": len(rows) - len(valid), "error_count": len(rows) - len(valid), "average_processing_time_seconds": sum(successful_times) / len(successful_times) if successful_times else None, "minimum_processing_time_seconds": min(successful_times) if successful_times else None, "maximum_processing_time_seconds": max(successful_times) if successful_times else None, "average_gtr_retrieval_seconds": sum(retrieval_times) / len(retrieval_times) if retrieval_times else None, "average_nli_inference_seconds": sum(nli_times) / len(nli_times) if nli_times else None, "retrieval_mode": "paper/GTR", "model": preflight["model"], "embedding_dimension": 768})
    destination = Path(output)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "predictions.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    csv_rows = [{key: (json.dumps(value) if isinstance(value, dict) else value) for key, value in row.items()} for row in rows]
    with (destination / "predictions.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(csv_rows[0]) if csv_rows else ["sample_id"])
        writer.writeheader()
        writer.writerows(csv_rows)
    report = {"dataset": str(dataset_path), "samples": len(rows), "sample_ids": [row["sample_id"] for row in rows], "seed": seed, "retrieval_model": preflight["model"], "retrieval_mode": "paper/GTR", "metrics": metrics, "cost": "Cost unavailable"}
    (destination / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (destination / "comparison_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    markdown = ["# GTR HaluEval Experiment", "", f"- Dataset: `{dataset_path}`", f"- Seed: {seed}", f"- Retrieval: paper/GTR (`{preflight['model']}`, 768 dimensions)", f"- Attempted: {metrics['attempted_samples']}", f"- Successful: {metrics['successful_samples']}", f"- Failed: {metrics['failed_samples']}", f"- Accuracy: {metrics['accuracy']}", f"- Precision: {metrics['precision']}", f"- Recall: {metrics['recall']}", f"- F1: {metrics['f1_score']}", f"- Confusion matrix: TP={metrics['tp']}, TN={metrics['tn']}, FP={metrics['fp']}, FN={metrics['fn']}", f"- Average successful-sample latency: {metrics['average_processing_time_seconds']}"]
    (destination / "report.md").write_text("\n".join(markdown) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Check optional paper-compatible HaluCheck retrieval")
    parser.add_argument("--output", default="results/paper_comparison")
    parser.add_argument("--run-gtr", action="store_true")
    parser.add_argument("--dataset")
    parser.add_argument("--samples", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--offline", action="store_true", help="Never contact Hugging Face; require the local GTR model.")
    args = parser.parse_args()
    if args.run_gtr:
        if not args.dataset:
            parser.error("--dataset is required with --run-gtr")
        destination = args.output if args.output != "results/paper_comparison" else f"results/halueval_gtr_{args.samples}"
        print(json.dumps(run_gtr_comparison(args.dataset, args.samples, args.seed, destination, offline=args.offline), indent=2))
    else:
        run_paper_preflight(args.output)


if __name__ == "__main__":
    main()
