from sources.adapters import GoogleFactCheckAdapter, WikidataAdapter
from sources.routing import deduplicate_evidence

def test_google_factcheck_requires_key(monkeypatch):
    monkeypatch.delenv("GOOGLE_FACT_CHECK_API_KEY", raising=False)
    assert not GoogleFactCheckAdapter().is_configured()

def test_wikidata_normalizes_mocked_response(monkeypatch):
    monkeypatch.setattr(WikidataAdapter, "_get", lambda self, *a, **k: {"search":[{"id":"Q1","label":"Paris","description":"capital"}]})
    result=WikidataAdapter().search("capital France")
    assert result[0].source == "Wikidata" and result[0].url.endswith("Q1")

def test_deduplication_removes_exact_normalized_duplicates():
    items=[{"title":"Paris","content":" Capital of France ","url":"u"},{"title":"Paris","content":"capital of france","url":"u"}]
    assert len(deduplicate_evidence(items)) == 1
