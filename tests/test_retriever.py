import numpy as np
import pytest
from services.vector_store import VectorStore, VectorStoreError

def test_vector_store_rejects_mismatched_metadata(tmp_path):
    store = VectorStore(tmp_path / "vector.index", tmp_path / "metadata.pkl")
    with pytest.raises(VectorStoreError, match="metadata"):
        store.build_index(np.zeros((2, 384), dtype=np.float32), [{"title": "One", "content": "Text"}])

def test_vector_store_requires_loaded_index(tmp_path):
    store = VectorStore(tmp_path / "vector.index", tmp_path / "metadata.pkl")
    with pytest.raises(VectorStoreError, match="Load"):
        store.search(np.zeros(384, dtype=np.float32))


class _Embedder:
    def encode(self, texts, **kwargs):
        return np.zeros((len(texts), 2), dtype=np.float32)


class _Store:
    _index = object()
    def search(self, embedding, top_k):
        from services.vector_store import Evidence
        return [Evidence("local", "weak local evidence", 0.10, 1)]


class _Wikipedia:
    def __init__(self): self.calls = []
    def retrieve(self, fact, top_k, query=None):
        from services.vector_store import Evidence
        self.calls.append((fact, top_k, query))
        return [Evidence("Python", "Python was created by Guido van Rossum.", 0.95, 1, "wikipedia", "https://example.test/Python")]


class _FailingWikipedia:
    def retrieve(self, fact, top_k, query=None):
        from services.wikipedia_service import WikipediaServiceError
        raise WikipediaServiceError("timeout")


def test_retriever_uses_wikipedia_only_when_local_evidence_is_weak():
    from services.retriever import EvidenceRetriever
    wikipedia = _Wikipedia()
    retriever = EvidenceRetriever(store=_Store(), wikipedia_service=wikipedia, local_similarity_threshold=0.60)
    retriever._embedder = _Embedder()
    result = retriever.retrieve("Python was created by Guido van Rossum.")
    assert result.used_wikipedia_fallback is True
    assert result.retrieved_evidence[0].source == "wikipedia"
    assert wikipedia.calls


def test_retriever_keeps_local_evidence_when_similarity_is_strong():
    from services.retriever import EvidenceRetriever
    wikipedia = _Wikipedia()
    retriever = EvidenceRetriever(store=_Store(), wikipedia_service=wikipedia, local_similarity_threshold=0.05)
    retriever._embedder = _Embedder()
    result = retriever.retrieve("A local fact.")
    assert result.used_wikipedia_fallback is False
    assert result.retrieved_evidence[0].source == "local"
    assert not wikipedia.calls


def test_retriever_falls_back_to_empty_evidence_when_wikipedia_times_out():
    from services.retriever import EvidenceRetriever
    retriever = EvidenceRetriever(store=_Store(), wikipedia_service=_FailingWikipedia(), local_similarity_threshold=0.60)
    retriever._embedder = _Embedder()

    result = retriever.retrieve("A fact that needs live evidence.")

    assert result.retrieved_evidence == []
    assert result.used_wikipedia_fallback is False


def test_retrieve_many_deduplicates_identical_fact_queries():
    from services.retriever import EvidenceRetriever
    wikipedia = _Wikipedia()
    retriever = EvidenceRetriever(store=_Store(), wikipedia_service=wikipedia, local_similarity_threshold=0.60)
    retriever._embedder = _Embedder()

    results = retriever.retrieve_many(["Same fact", "  same   fact  "])

    assert len(results) == 1
    assert len(wikipedia.calls) == 1


def test_paper_retrieval_mode_uses_separate_gtr_artifacts():
    from services.retriever import EvidenceRetriever

    retriever = EvidenceRetriever(retrieval_mode="paper", store=_Store())

    assert retriever.model_name == "sentence-transformers/gtr-t5-base"
    assert retriever.retrieval_mode == "paper"
    assert retriever.store is not None


def test_retrieval_mode_rejects_unknown_profile():
    from services.retriever import EvidenceRetriever

    with pytest.raises(ValueError, match="retrieval_mode"):
        EvidenceRetriever(retrieval_mode="unknown")
