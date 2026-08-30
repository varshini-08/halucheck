"""Validation and edge-case coverage for the completed Phase 1 and 2 modules."""

from __future__ import annotations

import json
import pickle
from unittest.mock import Mock, patch

import numpy as np
import pytest

from extraction.atomic_fact_extractor import AtomicFactExtractor
from services.llm_service import GroqProvider, LLMServiceException
from services.retriever import EvidenceRetriever, RetrievalError
from services.vector_store import VectorStore, VectorStoreError
from scripts.build_index import load_documents
from verification.entity_matcher import EntityMatcher


def test_llm_service_rejects_missing_key_and_empty_prompt() -> None:
    with pytest.raises(LLMServiceException, match="API key"):
        GroqProvider("").generate_response("Question")
    with pytest.raises(LLMServiceException, match="provide a question"):
        GroqProvider("test-key").generate_response("  ")


def test_llm_service_accepts_unicode_and_special_characters() -> None:
    completion = Mock(choices=[Mock(message=Mock(content="ok"))])
    with patch("services.llm_service.groq.Client") as client:
        client.return_value.chat.completions.create.return_value = completion
        assert GroqProvider("test-key").generate_response("தமிழ்? <script>😀</script>") == "ok"


@pytest.fixture(scope="module")
def extractor() -> AtomicFactExtractor:
    return AtomicFactExtractor()


@pytest.mark.parametrize("text", ["", "   ", "... !!!", "😀 😀", "12345"])
def test_fact_extraction_edge_inputs_do_not_crash(extractor: AtomicFactExtractor, text: str) -> None:
    facts = extractor.extract_atomic_facts(text)
    assert len({fact.fact_text for fact in facts}) == len(facts)


def test_fact_extraction_handles_bullets_dates_and_unicode(extractor: AtomicFactExtractor) -> None:
    text = "• Ada Lovelace wrote notes in 1843.\n• 東京 is in Japan."
    facts = extractor.extract_atomic_facts(text)
    assert facts
    assert any("1843" in fact.fact_text for fact in facts)
    assert len({fact.fact_text for fact in facts}) == len(facts)


def test_entity_matcher_handles_case_labels_and_empty_inputs() -> None:
    matcher = EntityMatcher(strict_label_matching=True)
    exact = matcher.compare_entities([{"text": "Apple", "label": "ORG"}], [{"text": " apple ", "label": "ORG"}])
    wrong_label = matcher.compare_entities([{"text": "Paris", "label": "GPE"}], [{"text": "Paris", "label": "PERSON"}])
    assert exact["factual_consistency_score"] == 100.0
    assert wrong_label["factual_consistency_score"] == 0.0
    assert matcher.compare_within_response([])["factual_consistency_score"] == 100.0


def test_knowledge_base_validation_handles_invalid_inputs(tmp_path) -> None:
    invalid_json = tmp_path / "broken.json"; invalid_json.write_text("{", encoding="utf-8")
    empty = tmp_path / "empty.json"; empty.write_text("[]", encoding="utf-8")
    invalid_schema = tmp_path / "schema.json"; invalid_schema.write_text(json.dumps([{"title": "only title"}]), encoding="utf-8")
    for path in (invalid_json, empty, invalid_schema, tmp_path / "missing.json"):
        with pytest.raises(VectorStoreError):
            load_documents(path)


def test_vector_store_persists_and_ranks_top_k(tmp_path) -> None:
    store = VectorStore(tmp_path / "index.faiss", tmp_path / "metadata.pkl")
    vectors = np.array([[1.0, 0.0], [0.0, 1.0], [0.8, 0.2]], dtype=np.float32)
    metadata = [{"title": "first", "content": "alpha"}, {"title": "second", "content": "beta"}, {"title": "third", "content": "alpha beta"}]
    store.build_index(vectors, metadata); store.save_index()
    loaded = VectorStore(store.index_path, store.metadata_path); loaded.load_index()
    evidence = loaded.search(np.array([1.0, 0.0], dtype=np.float32), top_k=3)
    assert [item.rank for item in evidence] == [1, 2, 3]
    assert evidence[0].title == "first"
    assert len(loaded.search(np.array([1.0, 0.0], dtype=np.float32), top_k=99)) == 3


def test_vector_store_rejects_corrupt_metadata_and_index(tmp_path) -> None:
    index_path, metadata_path = tmp_path / "index.faiss", tmp_path / "metadata.pkl"
    index_path.write_bytes(b"placeholder")
    metadata_path.write_bytes(b"not a pickle")
    with pytest.raises(VectorStoreError, match="metadata"):
        VectorStore(index_path, metadata_path).load_index()
    metadata_path.write_bytes(pickle.dumps([{"title": "document", "content": "text"}]))
    index_path.write_bytes(b"not a faiss index")
    with pytest.raises(VectorStoreError):
        VectorStore(index_path, metadata_path).load_index()


def test_retriever_validates_empty_fact_and_wraps_store_error(tmp_path) -> None:
    retriever = EvidenceRetriever(store=VectorStore(tmp_path / "missing.index", tmp_path / "missing.pkl"))
    with pytest.raises(ValueError, match="atomic fact"):
        retriever.retrieve(" ")
    with pytest.raises(RetrievalError, match="Vector index is missing"):
        retriever.retrieve("A valid fact")
