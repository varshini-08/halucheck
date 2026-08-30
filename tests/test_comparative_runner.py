import json
from types import SimpleNamespace

from evaluation import comparative_runner


class FakePipeline:
    def analyse(self, response, question=""):
        hallucination = response == "wrong"
        label = "CONTRADICTED" if hallucination else "SUPPORTED"
        result = SimpleNamespace(
            fact=response,
            label=label,
            confidence=0.8,
            hallucination=hallucination,
            reason="test result",
        )
        return SimpleNamespace(verifications=[result])


def test_comparison_reuses_identical_sample_ids_and_writes_outputs(tmp_path, monkeypatch):
    dataset = tmp_path / "dataset.jsonl"
    dataset.write_text(
        "\n".join(
            [
                json.dumps({"user_query": "q1", "llm_response": "right", "hallucination_label": False, "id": "one"}),
                json.dumps({"user_query": "q2", "llm_response": "wrong", "hallucination_label": True, "id": "two"}),
                json.dumps({"user_query": "q3", "llm_response": "right", "hallucination_label": False, "id": "three"}),
            ]
        ),
        encoding="utf-8",
    )
    configurations = tuple(
        comparative_runner.Configuration(name, name, FakePipeline)
        for name in comparative_runner.CONFIGURATIONS
    )
    monkeypatch.setattr(comparative_runner, "_configurations", lambda: configurations)

    comparison = comparative_runner.run_comparison(dataset, limit=2, seed=42, results_dir=tmp_path / "comparison")

    expected_ids = comparison["sample_ids"]
    assert len(expected_ids) == 2
    assert all(comparison["configurations"][name]["sample_ids"] == expected_ids for name in comparative_runner.CONFIGURATIONS)
    assert all(comparison["configurations"][name]["metrics"]["tp"] == 1 for name in comparative_runner.CONFIGURATIONS)
    assert all(comparison["configurations"][name]["metrics"]["tn"] == 1 for name in comparative_runner.CONFIGURATIONS)
    assert all(comparison["configurations"][name]["metrics"]["fp"] == 0 for name in comparative_runner.CONFIGURATIONS)
    assert all(comparison["configurations"][name]["metrics"]["fn"] == 0 for name in comparative_runner.CONFIGURATIONS)
    assert (tmp_path / "comparison" / "comparison.csv").exists()
    assert (tmp_path / "comparison" / "comparison_report.json").exists()
    assert all((tmp_path / "comparison" / name / "predictions.json").exists() for name in comparative_runner.CONFIGURATIONS)