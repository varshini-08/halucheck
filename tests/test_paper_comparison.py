from evaluation.paper_comparison import paper_preflight, run_paper_preflight


def test_paper_preflight_reports_missing_optional_artifacts(tmp_path):
    result = paper_preflight()

    assert result["retrieval_mode"] == "paper"
    assert result["model"] == "sentence-transformers/gtr-t5-base"
    assert result["status"].startswith("unavailable") or result["status"] == "ready"
    assert result["cost"] == "Cost unavailable"

    written = run_paper_preflight(tmp_path)
    assert (tmp_path / "preflight.json").exists()
    assert written == result