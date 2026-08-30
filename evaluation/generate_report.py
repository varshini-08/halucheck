from pathlib import Path
import json
def write_report(metrics, path, dataset, evaluated, average_time, retrieval, nli, comparison=None):
    report = {"dataset": str(dataset), "evaluated_samples": evaluated, "metrics": metrics, "average_processing_time_seconds": average_time, "retrieval_configuration": retrieval, "nli_model": nli}
    if comparison is not None: report["comparison"] = comparison
    Path(path).write_text(json.dumps(report, indent=2), encoding="utf-8"); return report
