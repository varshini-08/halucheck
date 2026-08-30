"""Isolated paper-style evaluation helpers.

The publication description does not fully specify the original decomposition and
aggregation implementation. These helpers therefore expose reproducible
approximations without changing the production pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from extraction.atomic_fact_extractor import AtomicFact, AtomicFactExtractor
from services.vector_store import Evidence
from verification.nli_verifier import NLIResult, NLIVerifier


class PaperMethodologyUnavailable(RuntimeError):
    """Raised when required paper-specific inputs are not available."""


class PaperAtomicFactExtractor:
    """Paper-mode adapter pending a fully specified public decomposition recipe."""

    mode = "paper-approximation"

    def __init__(self, extractor: AtomicFactExtractor | None = None) -> None:
        self.extractor = extractor or AtomicFactExtractor()

    def extract_atomic_facts(self, response: str) -> list[AtomicFact]:
        return self.extractor.extract_atomic_facts(response)


@dataclass(frozen=True)
class PaperFactDecision:
    fact: str
    label: str
    entailment_score: float
    contradiction_score: float
    neutral_score: float
    hallucination: bool


def aggregate_paper_style(
    fact: str,
    evidence_results: Sequence[tuple[Evidence, NLIResult]],
    threshold: float = 0.5,
) -> PaperFactDecision:
    """Average NLI probabilities across evidence for one fact.

    This is an explicit evaluation approximation of an average-entailment rule;
    it is intentionally separate from ``FactClassifier``.
    """
    if not evidence_results:
        return PaperFactDecision(fact, "NEUTRAL", 0.0, 0.0, 0.0, False)
    count = len(evidence_results)
    averages = {
        label: sum(result.probabilities.get(label, 0.0) for _, result in evidence_results) / count
        for label in ("SUPPORTED", "CONTRADICTED", "NEUTRAL")
    }
    label = max(averages, key=averages.get)
    hallucination = label == "CONTRADICTED" and averages[label] >= threshold
    return PaperFactDecision(
        fact,
        label,
        averages["SUPPORTED"],
        averages["CONTRADICTED"],
        averages["NEUTRAL"],
        hallucination,
    )
