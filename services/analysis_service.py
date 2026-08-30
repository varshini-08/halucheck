"""Orchestrates the HaluCheck Phase 1, 2, and 3 pipeline."""

from dataclasses import dataclass
import logging
import traceback
from time import perf_counter
from typing import Any, Callable, Dict, List, Optional

from debug.atomic_fact_debug import report_atomic_extraction
from extraction.atomic_fact_extractor import AtomicFact, AtomicFactExtractor
from services.retriever import EvidenceRetriever, FactRetrieval, RetrievalError
from verification.entity_matcher import EntityMatcher
from verification.fact_classifier import FactClassification
from verification.nli_verifier import NLIVerificationError
from verification.verification_pipeline import VerificationPipeline
from services.config import MAX_CLAIMS

LOGGER = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    response: str
    facts: List[AtomicFact]
    comparison: Dict[str, Any]
    retrievals: List[FactRetrieval]
    verifications: List[FactClassification]


class HaluCheckPipeline:
    """Extracts facts, retrieves evidence, then verifies it with NLI."""

    def __init__(
        self,
        retriever: Optional[EvidenceRetriever] = None,
        verification_pipeline: Optional[VerificationPipeline] = None,
    ) -> None:
        self.extractor = AtomicFactExtractor()
        self.matcher = EntityMatcher(strict_label_matching=True)
        self.retriever = retriever or EvidenceRetriever()
        self.verification_pipeline = verification_pipeline

    def analyse(
        self,
        response: str,
        question: str = "",
        progress_callback: Optional[Callable[[str], None]] = None,
        verification_callback: Optional[Callable[[FactClassification], None]] = None,
    ) -> AnalysisResult:
        pipeline_started = perf_counter()
        LOGGER.info("Entering HaluCheck analysis pipeline")
        print("Entering HaluCheck analysis pipeline", flush=True)
        if progress_callback:
            progress_callback("Extracting atomic facts...")
        extraction_started = perf_counter()
        facts = self.extractor.extract_atomic_facts(response, max_facts=MAX_CLAIMS)
        extraction_seconds = perf_counter() - extraction_started
        LOGGER.info("Atomic fact extraction completed in %.3fs", extraction_seconds)
        if progress_callback:
            progress_callback("Detecting entities...")
        try:
            report_atomic_extraction(question, response, facts)
        except OSError:
            pass
        entity_started = perf_counter()
        entities = [entity for fact in facts for entity in fact.entities]
        if progress_callback:
            progress_callback("Matching entities...")
        comparison = self.matcher.compare_within_response(entities)
        entity_seconds = perf_counter() - entity_started
        comparison["total_facts"] = len(facts)

        retrievals: List[FactRetrieval] = []
        verifications: List[FactClassification] = []
        retrieval_seconds = 0.0
        verification_seconds = 0.0
        if facts:
            if progress_callback:
                progress_callback("Retrieving evidence for atomic facts...")
            try:
                retrieval_started = perf_counter()
                retrievals = self.retriever.retrieve_many(facts)
                retrieval_seconds = perf_counter() - retrieval_started
                LOGGER.info("Evidence retrieval completed in %.3fs", retrieval_seconds)
            except RetrievalError as exc:
                comparison["retrieval_error"] = str(exc)
                LOGGER.exception("Evidence retrieval failed")
                traceback.print_exc()

        if not self.verification_pipeline:
            comparison["verification_error"] = "Verification pipeline was not configured."
            LOGGER.error("Verification pipeline was not configured")
        elif not retrievals:
            comparison["verification_error"] = "No retrieved facts were available for verification."
            LOGGER.warning("Skipping verification because no fact retrievals were produced")
        else:
            if progress_callback:
                progress_callback("Verifying facts against evidence...")
            try:
                LOGGER.info("Entering verification pipeline for %d fact(s)", len(retrievals))
                print(f"Entering verification pipeline for {len(retrievals)} fact(s)", flush=True)
                verification_started = perf_counter()
                verifications = self.verification_pipeline.verify_many(
                    retrievals, progress_callback=verification_callback
                )
                verification_seconds = perf_counter() - verification_started
                LOGGER.info("Fact classification completed in %.3fs", verification_seconds)
                print("Returning verification result", flush=True)
            except Exception as exc:
                comparison["verification_error"] = str(exc)
                LOGGER.exception("Verification pipeline failed")
                traceback.print_exc()

        total_seconds = perf_counter() - pipeline_started
        comparison["timings"] = {
            "extraction_seconds": extraction_seconds,
            "entity_seconds": entity_seconds,
            "local_faiss_seconds": getattr(self.retriever, "last_timings", {}).get("local_faiss_seconds", 0.0),
            "wikipedia_search_seconds": getattr(self.retriever, "last_timings", {}).get("wikipedia_search_seconds", 0.0),
            "wikipedia_article_seconds": getattr(self.retriever, "last_timings", {}).get("wikipedia_article_seconds", 0.0),
            "wikipedia_chunk_ranking_seconds": getattr(self.retriever, "last_timings", {}).get("wikipedia_chunk_ranking_seconds", 0.0),
            "retrieval_seconds": retrieval_seconds,
            "verification_seconds": verification_seconds,
            "nli_load_seconds": getattr(getattr(getattr(self.verification_pipeline, "classifier", None), "verifier", None), "last_timings", {}).get("nli_load_seconds", 0.0),
            "nli_inference_seconds": getattr(getattr(getattr(self.verification_pipeline, "classifier", None), "verifier", None), "last_timings", {}).get("nli_inference_seconds", 0.0),
            "total_seconds": total_seconds,
        }
        if self.retriever.retrieval_mode == "paper":
            comparison["retrieval_mode"] = "paper/GTR local FAISS index"
        else:
            comparison["retrieval_mode"] = "hybrid local knowledge base + Wikipedia fallback" if self.retriever.enable_wikipedia_fallback else "local knowledge base only"
        comparison["evidence_count"] = sum(len(item.retrieved_evidence) for item in retrievals)
        LOGGER.info("HaluCheck analysis pipeline completed in %.3fs", total_seconds)
        return AnalysisResult(response, facts, comparison, retrievals, verifications)


