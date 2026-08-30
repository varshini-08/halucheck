import pytest

from evaluation.baselines import BaselineUnavailable, SelfCheckNLIBaseline
from evaluation.llm_baseline import LLMJudge
from evaluation.paper_modes import PaperAtomicFactExtractor, aggregate_paper_style
from evaluation.performance import summarize_timings
from services.vector_store import Evidence
from verification.nli_verifier import NLIResult


def nli(label, supported, contradicted, neutral):
    return NLIResult(label, max(supported, contradicted, neutral), {"SUPPORTED": supported, "CONTRADICTED": contradicted, "NEUTRAL": neutral})


def test_paper_aggregator_averages_evidence_probabilities():
    evidence = [(Evidence("a", "one", 1.0, 1), nli("SUPPORTED", 0.8, 0.1, 0.1)), (Evidence("b", "two", 1.0, 2), nli("CONTRADICTED", 0.2, 0.7, 0.1))]

    decision = aggregate_paper_style("A fact.", evidence)

    assert decision.label == "SUPPORTED"
    assert decision.entailment_score == pytest.approx(0.5)
    assert decision.contradiction_score == pytest.approx(0.4)
    assert decision.hallucination is False


def test_selfcheck_requires_multiple_supplied_responses():
    with pytest.raises(BaselineUnavailable):
        SelfCheckNLIBaseline().score("A fact.", ["one response"])


def test_llm_judge_normalizes_label():
    class Service:
        def generate_response(self, prompt):
            return "NO_HALLUCINATION"

    assert LLMJudge(Service()).evaluate("q", "r").label == "no_hallucination"


def test_performance_summary_is_statistical():
    result = summarize_timings([1.0, 2.0, 3.0])
    assert result["average_seconds"] == pytest.approx(2.0)
    assert result["median_seconds"] == 2.0
    assert result["samples_per_second"] == pytest.approx(0.5)


def test_paper_extractor_is_explicit_adapter():
    assert PaperAtomicFactExtractor().mode == "paper-approximation"