"""Fact-level Phase 3 orchestration; retrieval itself remains unchanged."""

from __future__ import annotations

import logging
from time import perf_counter
from typing import Callable, Sequence

from services.retriever import FactRetrieval
from verification.fact_classifier import FactClassification, FactClassifier

LOGGER = logging.getLogger(__name__)


class VerificationPipeline:
    def __init__(self, classifier: FactClassifier | None = None) -> None:
        self.classifier = classifier or FactClassifier()

    def verify(self, retrieval: FactRetrieval) -> FactClassification:
        LOGGER.info("Entering verification pipeline for fact: %s", retrieval.fact)
        print(f"Verifying fact: {retrieval.fact}", flush=True)
        started = perf_counter()
        classification = self.classifier.classify(retrieval.fact, retrieval.retrieved_evidence)
        LOGGER.info("NLI verification for one fact completed in %.3fs", perf_counter() - started)
        return classification

    def verify_many(
        self,
        retrievals: Sequence[FactRetrieval],
        progress_callback: Callable[[FactClassification], None] | None = None,
    ) -> list[FactClassification]:
        started = perf_counter()
        LOGGER.info("Starting NLI verification for %d fact(s)", len(retrievals))
        print(f"Starting NLI verification for {len(retrievals)} fact(s)", flush=True)
        results = self.classifier.classify_many(
            [(retrieval.fact, retrieval.retrieved_evidence) for retrieval in retrievals]
        )
        if progress_callback:
            for result in results:
                progress_callback(result)
        LOGGER.info("Total Phase 3 verification completed in %.3fs", perf_counter() - started)
        return results
