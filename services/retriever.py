"""Hybrid fact-level evidence retrieval: local FAISS first, Wikipedia fallback."""
from __future__ import annotations
from dataclasses import dataclass
import logging
from pathlib import Path
from time import perf_counter
from typing import Any, Sequence

from extraction.atomic_fact_extractor import AtomicFact

from services.config import (
    CURRENT_RETRIEVAL_MODEL,
    ENABLE_WIKIPEDIA_FALLBACK,
    LOCAL_SIMILARITY_THRESHOLD,
    MAX_WIKIPEDIA_CHUNKS,
    PAPER_RETRIEVAL_MODEL,
)
from services.vector_store import Evidence, VectorStore, VectorStoreError
from services.wikipedia_service import WikipediaService, WikipediaServiceError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOGGER = logging.getLogger(__name__)


class RetrievalError(RuntimeError): pass


@dataclass(frozen=True)
class FactRetrieval:
    fact: str
    retrieved_evidence: list[Evidence]
    used_wikipedia_fallback: bool = False
    local_average_similarity: float = 0.0


class EvidenceRetriever:
    def __init__(self, model_name: str = CURRENT_RETRIEVAL_MODEL, store: VectorStore | None = None, wikipedia_service: WikipediaService | None = None, local_similarity_threshold: float = LOCAL_SIMILARITY_THRESHOLD, enable_wikipedia_fallback: bool = ENABLE_WIKIPEDIA_FALLBACK, retrieval_mode: str = "current", offline: bool = False) -> None:
        self.retrieval_mode = retrieval_mode.strip().lower()
        if self.retrieval_mode not in {"current", "paper"}:
            raise ValueError("retrieval_mode must be 'current' or 'paper'.")
        if self.retrieval_mode == "paper" and model_name == CURRENT_RETRIEVAL_MODEL:
            model_name = PAPER_RETRIEVAL_MODEL
        if self.retrieval_mode == "paper" and model_name != PAPER_RETRIEVAL_MODEL:
            raise ValueError("Paper retrieval mode requires sentence-transformers/gtr-t5-base.")
        self.model_name = model_name
        self.offline = bool(offline)
        default_index = "gtr_base.index" if self.retrieval_mode == "paper" else "vector.index"
        default_metadata = "gtr_base_metadata.pkl" if self.retrieval_mode == "paper" else "metadata.pkl"
        self.store = store or VectorStore(PROJECT_ROOT / "vector_db" / default_index, PROJECT_ROOT / "vector_db" / default_metadata)
        self._embedder: Any | None = None
        self._embedding_cache: dict[str, Any] = {}
        self._retrieval_cache: dict[tuple[str, str, int], FactRetrieval] = {}
        self.cache_hits = 0
        self.cache_misses = 0
        self.wikipedia_service = wikipedia_service
        self.local_similarity_threshold = local_similarity_threshold
        # Offline evaluation must be hermetic: no live Wikipedia call can occur.
        self.enable_wikipedia_fallback = bool(enable_wikipedia_fallback) and not self.offline
        self.last_timings: dict[str, float] = {
            "local_faiss_seconds": 0.0,
            "wikipedia_search_seconds": 0.0,
            "wikipedia_article_seconds": 0.0,
            "wikipedia_chunk_ranking_seconds": 0.0,
            "total_evidence_retrieval_seconds": 0.0,
        }

    def _get_embedder(self) -> Any:
        if self._embedder is None:
            try:
                from sentence_transformers import SentenceTransformer
                try:
                    self._embedder = SentenceTransformer(self.model_name, local_files_only=True)
                except Exception:
                    if self.offline:
                        raise RetrievalError(
                            "Offline sentence-transformer model unavailable: " + self.model_name
                        )
                    self._embedder = SentenceTransformer(self.model_name)
            except Exception as exc:
                raise RetrievalError("Unable to load the sentence-transformer model.") from exc
        return self._embedder

    def _wikipedia(self) -> WikipediaService:
        if self.wikipedia_service is None:
            self.wikipedia_service = WikipediaService(self._get_embedder())
        return self.wikipedia_service

    @staticmethod
    def _normalise_cache_text(text: str) -> str:
        return " ".join(text.casefold().split())

    def _embedding_for(self, fact: str) -> Any:
        key = self._normalise_cache_text(fact)
        if key not in self._embedding_cache:
            self._embedding_cache[key] = self._get_embedder().encode(
                [fact], convert_to_numpy=True, show_progress_bar=False
            )[0]
        return self._embedding_cache[key]

    def retrieve(self, fact: str, top_k: int = 3, wikipedia_query: str | None = None) -> FactRetrieval:
        total_started = perf_counter()
        if not fact or not fact.strip():
            raise ValueError("An atomic fact is required for retrieval.")
        cache_key = (self._normalise_cache_text(fact), self._normalise_cache_text(wikipedia_query or fact), top_k)
        cached = self._retrieval_cache.get(cache_key)
        if cached is not None:
            self.cache_hits += 1
            return FactRetrieval(fact, list(cached.retrieved_evidence), cached.used_wikipedia_fallback, cached.local_average_similarity)
        self.cache_misses += 1
        try:
            local_started = perf_counter()
            if self.store._index is None:
                self.store.load_index()
            local = self.store.search(self._embedding_for(fact), top_k)
            local_seconds = perf_counter() - local_started
            LOGGER.info("Local FAISS retrieval completed in %.3fs", local_seconds)
        except VectorStoreError as exc:
            raise RetrievalError(str(exc)) from exc
        average = sum(item.score for item in local) / len(local) if local else 0.0
        if not self.enable_wikipedia_fallback or local and average >= self.local_similarity_threshold:
            result = FactRetrieval(fact, local, False, average)
            self._retrieval_cache[cache_key] = result
            self.last_timings = {
                "local_faiss_seconds": local_seconds,
                "wikipedia_search_seconds": 0.0,
                "wikipedia_article_seconds": 0.0,
                "wikipedia_chunk_ranking_seconds": 0.0,
                "total_evidence_retrieval_seconds": perf_counter() - total_started,
            }
            LOGGER.info("Total evidence retrieval completed in %.3fs", self.last_timings["total_evidence_retrieval_seconds"])
            return result
        try:
            if wikipedia_query:
                live = self._wikipedia().retrieve(fact, query=wikipedia_query, top_k=min(top_k, MAX_WIKIPEDIA_CHUNKS))
            else:
                # Keep the public call compatible with existing retriever clients.
                live = self._wikipedia().retrieve(fact, top_k=min(top_k, MAX_WIKIPEDIA_CHUNKS))
            if live:
                result = FactRetrieval(fact, live, True, average)
                self._retrieval_cache[cache_key] = result
                wikipedia_timings = getattr(self._wikipedia(), "last_timings", {})
                self.last_timings = {
                    "local_faiss_seconds": local_seconds,
                    "wikipedia_search_seconds": wikipedia_timings.get("wikipedia_search_seconds", 0.0),
                    "wikipedia_article_seconds": wikipedia_timings.get("wikipedia_article_seconds", 0.0),
                    "wikipedia_chunk_ranking_seconds": wikipedia_timings.get("wikipedia_chunk_ranking_seconds", 0.0),
                    "total_evidence_retrieval_seconds": perf_counter() - total_started,
                }
                LOGGER.info("Total evidence retrieval completed in %.3fs", self.last_timings["total_evidence_retrieval_seconds"])
                return result
        except WikipediaServiceError:
            # Local evidence remains useful even if live verification is unavailable.
            pass
        # Below-threshold local matches are unrelated evidence, not useful NLI input.
        result = FactRetrieval(fact, local if average >= self.local_similarity_threshold else [], False, average)
        self._retrieval_cache[cache_key] = result
        self.last_timings = {
            "local_faiss_seconds": local_seconds,
            "wikipedia_search_seconds": 0.0,
            "wikipedia_article_seconds": 0.0,
            "wikipedia_chunk_ranking_seconds": 0.0,
            "total_evidence_retrieval_seconds": perf_counter() - total_started,
        }
        LOGGER.info("Total evidence retrieval completed in %.3fs", self.last_timings["total_evidence_retrieval_seconds"])
        return result

    def retrieve_many(self, facts: Sequence[str | AtomicFact], top_k: int = 3) -> list[FactRetrieval]:
        retrievals: list[FactRetrieval] = []
        seen: set[tuple[str, str, int]] = set()
        for item in facts:
            if isinstance(item, AtomicFact):
                fact = item.fact_text
                # Search with the complete claim rather than an isolated entity.
                # Entity-only queries can resolve to disambiguation pages (for
                # example, “Newton”) and produce semantically irrelevant evidence.
                query = fact
            else:
                fact, query = item, item
            if fact and fact.strip():
                cache_key = (self._normalise_cache_text(fact), self._normalise_cache_text(query), top_k)
                if cache_key in seen:
                    continue
                seen.add(cache_key)
                retrievals.append(self.retrieve(fact, top_k, wikipedia_query=query))
        return retrievals

    def retrieve_context(self, query: str, top_k: int = 3) -> str:
        return "\n\n".join(item.content for item in self.retrieve(query, top_k).retrieved_evidence)
