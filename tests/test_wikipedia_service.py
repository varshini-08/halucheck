import numpy as np
import pytest
from services.wikipedia_service import WikipediaService, WikipediaServiceError


class FakeResponse:
    def __init__(self, payload): self.payload = payload
    def raise_for_status(self): pass
    def json(self): return self.payload


class FakeSession:
    def __init__(self): self.headers = {}; self.calls = 0
    def get(self, url, params, timeout):
        self.calls += 1
        if params.get("list") == "search":
            return FakeResponse({"query": {"search": [{"title": "Python", "pageid": 123}]}})
        return FakeResponse({"query": {"pages": [{"title": "Python", "extract": "Python is a programming language. " * 300}]}})


class Embedder:
    def encode(self, texts, **kwargs):
        return np.array([[1.0, 0.0] if "programming" in text.lower() or text == texts[0] else [0.0, 1.0] for text in texts])


def service():
    instance = WikipediaService(Embedder())
    instance.session = FakeSession()
    return instance


def test_search_article_chunk_and_cache():
    instance = service()
    assert instance.search("Python") == ("Python", 123)
    assert instance.search("Python") == ("Python", 123)
    article = instance.article("Python", 123)
    assert article and article.title == "Python"
    assert len(instance.chunk_text(article.extract, max_words=100)) == 15
    assert instance.session.calls == 2


def test_live_evidence_is_ranked_and_labeled():
    evidence = service().retrieve("Python programming language", top_k=2, max_words=100)
    assert len(evidence) == 2
    assert all(item.source == "wikipedia" and item.url for item in evidence)


def test_normalized_query_and_ranking_cache_avoid_repeat_work():
    instance = service()
    first = instance.retrieve("Python programming language", query="Python", top_k=2, max_words=100)
    second = instance.retrieve("Python programming language", query=" python ", top_k=2, max_words=100)

    assert first == second
    assert instance.session.calls == 2
    assert set(instance.last_timings) == {
        "wikipedia_search_seconds",
        "wikipedia_article_seconds",
        "wikipedia_chunk_ranking_seconds",
        "wikipedia_total_seconds",
    }


def test_invalid_response_is_safe():
    instance = service()
    instance.session.get = lambda *args, **kwargs: FakeResponse([])
    with pytest.raises(WikipediaServiceError):
        instance.search("Python")
