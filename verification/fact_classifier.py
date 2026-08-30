"""Evidence-level NLI aggregation for one atomic fact."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Sequence

from services.vector_store import Evidence
from verification.nli_verifier import NLIResult, NLIVerifier

STRONG_NLI_CONFIDENCE = 0.70
LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class EvidenceVerification:
    evidence: Evidence
    result: NLIResult


@dataclass(frozen=True)
class FactClassification:
    fact: str
    label: str
    confidence: float
    best_evidence: Evidence | None
    hallucination: bool
    reason: str
    evidence_verifications: list[EvidenceVerification]


class FactClassifier:
    """Combines retrieved evidence with model-derived NLI scores."""

    def __init__(self, verifier: NLIVerifier | None = None, threshold: float = STRONG_NLI_CONFIDENCE) -> None:
        self.verifier = verifier or NLIVerifier()
        self.threshold = threshold

    def _classify_outcomes(self, fact: str, outcomes: list[EvidenceVerification]) -> FactClassification:
        supported = [item for item in outcomes if item.result.label == "SUPPORTED" and item.result.confidence >= self.threshold]
        contradicted = [item for item in outcomes if item.result.label == "CONTRADICTED" and item.result.confidence >= self.threshold]
        if supported and contradicted:
            best_support = max(supported, key=lambda item: item.result.confidence)
            best_contradiction = max(contradicted, key=lambda item: item.result.confidence)
            if best_contradiction.result.confidence > best_support.result.confidence:
                return FactClassification(fact, "CONTRADICTED", best_contradiction.result.confidence, best_contradiction.evidence, True, "The strongest retrieved NLI result contradicts this fact.", outcomes)
        if supported:
            best = max(supported, key=lambda item: item.result.confidence)
            return FactClassification(fact, "SUPPORTED", best.result.confidence, best.evidence, False, "At least one retrieved passage entails this fact.", outcomes)
        if contradicted:
            best = max(contradicted, key=lambda item: item.result.confidence)
            return FactClassification(fact, "CONTRADICTED", best.result.confidence, best.evidence, True, "At least one retrieved passage contradicts this fact.", outcomes)
        neutral_candidates = [item for item in outcomes if item.result.label == "NEUTRAL"]
        best = max(neutral_candidates or outcomes, key=lambda item: item.result.confidence, default=None)
        confidence = best.result.confidence if best else 0.0
        return FactClassification(fact, "NEUTRAL", confidence, best.evidence if best else None, False, "Retrieved evidence is insufficient to support or contradict this fact.", outcomes)

    def classify_many(self, fact_evidence_items: Sequence[tuple[str, Sequence[Evidence]]]) -> list[FactClassification]:
        """Batch NLI work while keeping the existing fact-level decision rules."""
        pairs = [(evidence.content, fact) for fact, evidence_items in fact_evidence_items for evidence in evidence_items]
        if hasattr(self.verifier, "verify_many"):
            nli_results = self.verifier.verify_many(pairs)
        else:
            # Retains compatibility with test doubles and custom verifier adapters.
            nli_results = [self.verifier.verify(premise, hypothesis) for premise, hypothesis in pairs]
        iterator = iter(nli_results)
        classifications: list[FactClassification] = []
        for fact, evidence_items in fact_evidence_items:
            outcomes = [EvidenceVerification(evidence, next(iterator)) for evidence in evidence_items]
            classifications.append(self._classify_outcomes(fact, outcomes))
        return classifications

    def classify(self, fact: str, evidence_items: Sequence[Evidence]) -> FactClassification:
        LOGGER.info("Entering fact classifier for %r with %d evidence item(s)", fact, len(evidence_items))
        print(f"Entering fact classifier ({len(evidence_items)} evidence item(s))", flush=True)
        outcomes: list[EvidenceVerification] = []
        for index, evidence in enumerate(evidence_items, start=1):
            LOGGER.info("Starting NLI inference for evidence %d", index)
            print(f"Starting NLI inference for evidence {index}", flush=True)
            outcomes.append(EvidenceVerification(evidence, self.verifier.verify(evidence.content, fact)))
            LOGGER.info("NLI inference completed for evidence %d", index)
            print(f"NLI inference completed for evidence {index}", flush=True)
        return self._classify_outcomes(fact, outcomes)
