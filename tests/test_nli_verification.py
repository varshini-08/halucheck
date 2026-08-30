from services.retriever import FactRetrieval
from services.vector_store import Evidence
from verification.fact_classifier import FactClassifier
from verification.nli_verifier import NLIResult, NLIVerifier
from verification.verification_pipeline import VerificationPipeline
from visualization.dashboard import _severity


class FakeVerifier:
    def verify(self, premise: str, hypothesis: str) -> NLIResult:
        if "supports" in premise:
            return NLIResult("SUPPORTED", 0.95, {"SUPPORTED": 0.95, "CONTRADICTED": 0.02, "NEUTRAL": 0.03})
        if "contradicts" in premise:
            return NLIResult("CONTRADICTED", 0.91, {"SUPPORTED": 0.03, "CONTRADICTED": 0.91, "NEUTRAL": 0.06})
        return NLIResult("NEUTRAL", 0.76, {"SUPPORTED": 0.11, "CONTRADICTED": 0.13, "NEUTRAL": 0.76})


def evidence(content: str) -> Evidence:
    return Evidence("source", content, 0.8, 1)


def test_classifier_prioritizes_strong_support_over_contradiction():
    result = FactClassifier(FakeVerifier()).classify("A fact.", [evidence("contradicts"), evidence("supports")])

    assert result.label == "SUPPORTED"
    assert result.hallucination is False
    assert result.confidence == 0.95


def test_classifier_marks_strong_contradiction_as_hallucination():
    result = FactClassifier(FakeVerifier()).classify("A fact.", [evidence("contradicts")])

    assert result.label == "CONTRADICTED"
    assert result.hallucination is True


def test_classifier_returns_neutral_when_evidence_is_insufficient():
    result = FactClassifier(FakeVerifier()).classify("A fact.", [evidence("unrelated")])

    assert result.label == "NEUTRAL"
    assert result.hallucination is False


def test_verification_pipeline_preserves_fact_and_evidence():
    retrieval = FactRetrieval("A fact.", [evidence("supports")])
    result = VerificationPipeline(FactClassifier(FakeVerifier())).verify_many([retrieval])

    assert result[0].fact == "A fact."
    assert result[0].best_evidence is not None


def test_nli_label_normalization_is_model_label_agnostic():
    assert NLIVerifier._canonical_label("entailment") == "SUPPORTED"
    assert NLIVerifier._canonical_label("CONTRADICTION") == "CONTRADICTED"
    assert NLIVerifier._canonical_label("neutral") == "NEUTRAL"


def test_dashboard_severity_is_explicitly_heuristic():
    assert _severity(0, 0, 0.0) == "Unknown"
    assert _severity(0, 3, 0.95) == "Low"
    assert _severity(1, 3, 0.60) == "Medium"
    assert _severity(2, 3, 0.60) == "High"
