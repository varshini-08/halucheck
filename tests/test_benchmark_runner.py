import json
from types import SimpleNamespace

from evaluation.benchmark_runner import run_benchmark


class FakePipeline:
    def __init__(self):
        self.calls = []

    def analyse(self, response, question=""):
        self.calls.append((response, question))
        label = "CONTRADICTED" if "wrong" in response else "SUPPORTED"
        classification = SimpleNamespace(
            fact=response,
            label=label,
            confidence=0.9,
            hallucination=label == "CONTRADICTED",
            reason="test result",
        )
        return SimpleNamespace(verifications=[classification])


def test_benchmark_verifies_supplied_responses_and_writes_required_outputs(tmp_path):
    dataset = tmp_path / "dataset.jsonl"
    dataset.write_text(
        "\n".join(
            [
                json.dumps({"user_query": "q1", "llm_response": "right", "hallucination_label": False}),
                json.dumps({"user_query": "q2", "llm_response": "wrong", "hallucination_label": True}),
            ]
        ),
        encoding="utf-8",
    )
    output = tmp_path / "halueval_2"
    pipeline = FakePipeline()

    metrics, rows = run_benchmark(dataset, limit=2, seed=42, pipeline=pipeline, results_dir=output)

    assert pipeline.calls == [("wrong", "q2"), ("right", "q1")]
    assert [row["fact_count"] for row in rows] == [1, 1]
    assert all(row["supported_fact_count"] + row["contradicted_fact_count"] == 1 for row in rows)
    assert metrics["tp"] == 1
    assert metrics["tn"] == 1
    assert metrics["fp"] == 0
    assert metrics["fn"] == 0
    assert metrics["failed_samples"] == 0
    assert all((output / name).exists() for name in ("predictions.json", "predictions.csv", "metrics.json", "report.json"))


def test_benchmark_continues_after_one_pipeline_failure(tmp_path):
    dataset = tmp_path / "dataset.jsonl"
    dataset.write_text(
        "\n".join(
            [
                json.dumps({"user_query": "q1", "llm_response": "ok", "hallucination_label": False}),
                json.dumps({"user_query": "q2", "llm_response": "fails", "hallucination_label": True}),
            ]
        ),
        encoding="utf-8",
    )

    class FailingPipeline(FakePipeline):
        def analyse(self, response, question=""):
            if response == "fails":
                raise RuntimeError("test failure")
            return super().analyse(response, question)

    metrics, rows = run_benchmark(dataset, limit=2, seed=42, pipeline=FailingPipeline(), results_dir=tmp_path / "output")

    assert len(rows) == 2
    assert metrics["failed_samples"] == 1
    assert any(row["predicted_label"] == "error" and row["error"] == "test failure" for row in rows)