"""Persistent FAISS vector-store primitives used by the retrieval layer."""
from __future__ import annotations
import logging
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence
import numpy as np

LOGGER = logging.getLogger(__name__)
class VectorStoreError(RuntimeError):
    """Raised when a persisted vector index cannot be used safely."""

@dataclass(frozen=True)
class Evidence:
    title: str
    content: str
    score: float
    rank: int
    source: str = "local"
    url: str | None = None

class VectorStore:
    """Stores normalized embeddings and aligned document metadata in FAISS."""
    def __init__(self, index_path: Path | str, metadata_path: Path | str) -> None:
        self.index_path, self.metadata_path = Path(index_path), Path(metadata_path)
        self._index: Any | None = None
        self._metadata: list[dict[str, str]] = []
    @staticmethod
    def _faiss() -> Any:
        try:
            import faiss
            return faiss
        except ImportError as exc:
            raise VectorStoreError("FAISS is not installed. Run: pip install -r requirements.txt") from exc
    def build_index(self, embeddings: np.ndarray, metadata: Sequence[dict[str, str]]) -> None:
        vectors = np.asarray(embeddings, dtype=np.float32)
        if vectors.ndim != 2 or vectors.shape[0] == 0:
            raise VectorStoreError("Embeddings must be a non-empty two-dimensional array.")
        if vectors.shape[0] != len(metadata):
            raise VectorStoreError("Every embedding must have exactly one metadata record.")
        if any(not item.get("title") or not item.get("content") for item in metadata):
            raise VectorStoreError("Metadata records require non-empty title and content fields.")
        faiss = self._faiss(); faiss.normalize_L2(vectors)
        self._index = faiss.IndexFlatIP(vectors.shape[1]); self._index.add(vectors)
        self._metadata = [{"title": item["title"], "content": item["content"]} for item in metadata]
    def save_index(self) -> None:
        if self._index is None: raise VectorStoreError("Build or load an index before saving it.")
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self._faiss().write_index(self._index, str(self.index_path))
        with self.metadata_path.open("wb") as handle: pickle.dump(self._metadata, handle, protocol=pickle.HIGHEST_PROTOCOL)
        LOGGER.info("Saved vector index with %d documents", len(self._metadata))
    def load_index(self) -> None:
        if not self.index_path.exists() or not self.metadata_path.exists():
            raise VectorStoreError("Vector index is missing. Build it with: python scripts/build_index.py")
        try:
            with self.metadata_path.open("rb") as handle: metadata = pickle.load(handle)
        except (OSError, pickle.UnpicklingError) as exc: raise VectorStoreError("Unable to read vector index metadata.") from exc
        if not isinstance(metadata, list) or not metadata: raise VectorStoreError("Vector index metadata is empty or invalid.")
        try:
            index = self._faiss().read_index(str(self.index_path))
        except (OSError, RuntimeError) as exc:
            raise VectorStoreError("Unable to read FAISS vector index.") from exc
        if index.ntotal != len(metadata): raise VectorStoreError("Vector index and metadata have different document counts.")
        self._index, self._metadata = index, metadata
    def search(self, query_embedding: np.ndarray, top_k: int = 3) -> list[Evidence]:
        if self._index is None: raise VectorStoreError("Load the vector index before searching.")
        if top_k < 1: raise ValueError("top_k must be at least 1.")
        query = np.asarray(query_embedding, dtype=np.float32).reshape(1, -1)
        if query.shape[1] != self._index.d: raise VectorStoreError("Query dimension does not match index dimension.")
        faiss = self._faiss(); faiss.normalize_L2(query)
        scores, ids = self._index.search(query, min(top_k, len(self._metadata)))
        return [Evidence(self._metadata[idx]["title"], self._metadata[idx]["content"], float(score), rank) for rank, (score, idx) in enumerate(zip(scores[0], ids[0]), 1) if idx >= 0]
