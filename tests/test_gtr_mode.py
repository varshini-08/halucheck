from services.retriever import EvidenceRetriever, RetrievalError
from evaluation.paper_comparison import paper_preflight

def test_paper_mode_selects_gtr_and_separate_paths():
    retriever = EvidenceRetriever(retrieval_mode="paper")
    assert retriever.model_name == "sentence-transformers/gtr-t5-base"
    assert retriever.store.index_path.name == "gtr_base.index"
    assert retriever.store.metadata_path.name == "gtr_base_metadata.pkl"

def test_gtr_preflight_is_truthful_when_index_is_missing():
    result = paper_preflight()
    if not result["index_available"]:
        assert result["status"].startswith("unavailable")
