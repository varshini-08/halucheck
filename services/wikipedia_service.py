"""Cached, API-only Wikipedia evidence retrieval for hybrid verification."""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import html
import logging
import os
import re
from time import perf_counter
from typing import Any

import numpy as np
import requests

from services.vector_store import Evidence
from services.config import EVIDENCE_RELEVANCE_THRESHOLD

LOGGER = logging.getLogger(__name__)
WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"


class WikipediaServiceError(RuntimeError):
    """Raised when live Wikipedia evidence cannot be retrieved safely."""


@dataclass(frozen=True)
class WikipediaArticle:
    title: str
    url: str
    extract: str


class WikipediaService:
    """Searches and ranks plain-text Wikipedia extracts without HTML scraping."""

    def __init__(self, embedder: Any, timeout: float | None = None, user_agent: str | None = None) -> None:
        self.embedder = embedder
        self.timeout = timeout if timeout is not None else float(os.getenv("WIKIPEDIA_REQUEST_TIMEOUT", "10"))
        self.user_agent = user_agent or os.getenv("WIKIPEDIA_USER_AGENT", "HaluCheck/1.0 (Educational Project)")
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent, "Accept": "application/json"})
        self._ranking_cache: dict[tuple[str, str, int, int], list[Evidence]] = {}
        self.last_timings: dict[str, float] = {
            "wikipedia_search_seconds": 0.0,
            "wikipedia_article_seconds": 0.0,
            "wikipedia_chunk_ranking_seconds": 0.0,
            "wikipedia_total_seconds": 0.0,
        }

    @staticmethod
    def _normalise_query(query: str) -> str:
        return " ".join(query.casefold().split())

    def _request(self, params: dict[str, str]) -> dict[str, Any]:
        try:
            response = self.session.get(WIKIPEDIA_API, params=params, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise WikipediaServiceError("Wikipedia is temporarily unavailable.") from exc
        if not isinstance(payload, dict):
            raise WikipediaServiceError("Wikipedia returned an invalid response.")
        return payload

    @lru_cache(maxsize=128)
    def search(self, query: str) -> tuple[str, int] | None:
        started = perf_counter()
        payload = self._request({"action": "query", "list": "search", "srsearch": query, "srlimit": "1", "format": "json", "formatversion": "2"})
        results = payload.get("query", {}).get("search", [])
        LOGGER.info("Wikipedia search completed in %.3fs", perf_counter() - started)
        if not results or not isinstance(results[0], dict) or not results[0].get("title") or not results[0].get("pageid"):
            return None
        return str(results[0]["title"]), int(results[0]["pageid"])

    @lru_cache(maxsize=128)
    def article(self, title: str, page_id: int) -> WikipediaArticle | None:
        started = perf_counter()
        payload = self._request({"action": "query", "prop": "extracts", "pageids": str(page_id), "explaintext": "1", "exsectionformat": "plain", "format": "json", "formatversion": "2"})
        pages = payload.get("query", {}).get("pages", [])
        LOGGER.info("Wikipedia article retrieval completed in %.3fs", perf_counter() - started)
        if not pages or not isinstance(pages[0], dict):
            return None
        extract = self.clean_text(str(pages[0].get("extract", "")))
        if not extract:
            return None
        page_title = str(pages[0].get("title") or title)
        return WikipediaArticle(page_title, f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}", extract)

    @staticmethod
    def clean_text(text: str) -> str:
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        text = re.sub(r"\[\d+\]", "", text)
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def chunk_text(text: str, max_words: int = 450) -> list[str]:
        words = text.split()
        return [" ".join(words[index : index + max_words]) for index in range(0, len(words), max_words) if words[index : index + max_words]]

    def retrieve(self, fact: str, query: str | None = None, top_k: int = 3, max_words: int = 450) -> list[Evidence]:
        total_started = perf_counter()
        search_started = perf_counter()
        search_result = self.search(self._normalise_query(query or fact))
        search_seconds = perf_counter() - search_started
        if not search_result:
            self.last_timings = {
                "wikipedia_search_seconds": search_seconds,
                "wikipedia_article_seconds": 0.0,
                "wikipedia_chunk_ranking_seconds": 0.0,
                "wikipedia_total_seconds": perf_counter() - total_started,
            }
            return []
        article_started = perf_counter()
        article = self.article(*search_result)
        article_seconds = perf_counter() - article_started
        if not article:
            self.last_timings = {
                "wikipedia_search_seconds": search_seconds,
                "wikipedia_article_seconds": article_seconds,
                "wikipedia_chunk_ranking_seconds": 0.0,
                "wikipedia_total_seconds": perf_counter() - total_started,
            }
            return []
        chunks = self.chunk_text(article.extract, max_words)
        if not chunks:
            self.last_timings = {
                "wikipedia_search_seconds": search_seconds,
                "wikipedia_article_seconds": article_seconds,
                "wikipedia_chunk_ranking_seconds": 0.0,
                "wikipedia_total_seconds": perf_counter() - total_started,
            }
            return []
        cache_key = (str(search_result[1]), self._normalise_query(fact), top_k, max_words)
        cached = self._ranking_cache.get(cache_key)
        if cached is not None:
            self.last_timings = {
                "wikipedia_search_seconds": search_seconds,
                "wikipedia_article_seconds": article_seconds,
                "wikipedia_chunk_ranking_seconds": 0.0,
                "wikipedia_total_seconds": perf_counter() - total_started,
            }
            return list(cached)
        started = perf_counter()
        vectors = np.asarray(self.embedder.encode([fact, *chunks], convert_to_numpy=True, show_progress_bar=False), dtype=np.float32)
        query, chunk_vectors = vectors[0], vectors[1:]
        query /= max(float(np.linalg.norm(query)), 1e-12)
        chunk_vectors /= np.maximum(np.linalg.norm(chunk_vectors, axis=1, keepdims=True), 1e-12)
        scores = chunk_vectors @ query
        order = np.argsort(-scores)[:top_k]
        ranking_seconds = perf_counter() - started
        LOGGER.info("Wikipedia chunk ranking completed in %.3fs", ranking_seconds)
        evidence = [Evidence(article.title, chunks[index], float(scores[index]), rank, "wikipedia", article.url) for rank, index in enumerate(order, 1) if float(scores[index]) >= EVIDENCE_RELEVANCE_THRESHOLD]
        self._ranking_cache[cache_key] = evidence
        self.last_timings = {
            "wikipedia_search_seconds": search_seconds,
            "wikipedia_article_seconds": article_seconds,
            "wikipedia_chunk_ranking_seconds": ranking_seconds,
            "wikipedia_total_seconds": perf_counter() - total_started,
        }
        LOGGER.info(
            "Wikipedia retrieval timings: search=%.3fs article=%.3fs ranking=%.3fs total=%.3fs",
            search_seconds,
            article_seconds,
            ranking_seconds,
            self.last_timings["wikipedia_total_seconds"],
        )
        return list(evidence)
