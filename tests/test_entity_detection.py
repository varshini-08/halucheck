import pytest
from entity_detection import EntityDetector, EntityMatcher

@pytest.fixture(scope="module")
def detector():
    """Initializes the entity detector once for all tests."""
    return EntityDetector("en_core_web_sm")

@pytest.fixture
def matcher():
    """Initializes the matcher before each test."""
    return EntityMatcher(similarity_threshold=80.0, type_matching=True)


def test_entity_extraction_basic(detector):
    """Verify standard entities are extracted correctly."""
    text = "Steve Jobs founded Apple in Cupertino in 1976."
    entities = detector.extract_entities(text)
    
    # We expect Steve Jobs (PERSON), Apple (ORG), Cupertino (GPE), 1976 (DATE)
    entity_texts = [ent["text"] for ent in entities]
    entity_labels = [ent["label"] for ent in entities]
    
    assert "Steve Jobs" in entity_texts
    assert "Apple" in entity_texts
    assert "Cupertino" in entity_texts
    assert "1976" in entity_texts
    
    # Check that basic metadata is captured
    first_ent = entities[0]
    assert "text" in first_ent
    assert "label" in first_ent
    assert "start" in first_ent
    assert "end" in first_ent
    assert "sentence" in first_ent


def test_entity_extraction_filtering(detector):
    """Verify that label filtering works."""
    text = "Steve Jobs founded Apple in Cupertino in 1976."
    
    # Extract only PERSON and ORG
    entities = detector.extract_entities(text, entity_types=["PERSON", "ORG"])
    entity_labels = [ent["label"] for ent in entities]
    
    assert "PERSON" in entity_labels
    assert "ORG" in entity_labels
    assert "GPE" not in entity_labels
    assert "DATE" not in entity_labels


def test_matcher_exact_match(matcher):
    """Verify exact match checks return 100% consistency."""
    source_entities = [{"text": "Apple", "label": "ORG"}]
    response_entities = [{"text": "Apple", "label": "ORG"}]
    
    result = matcher.compare_entities(source_entities, response_entities)
    
    assert result["factual_consistency_score"] == 100.0
    assert len(result["verified"]) == 1
    assert len(result["hallucinated"]) == 0
    assert result["verified"][0]["similarity_score"] == 100.0


def test_matcher_fuzzy_match(matcher):
    """Verify fuzzy matching maps similar names correctly."""
    source_entities = [{"text": "Google LLC", "label": "ORG"}]
    response_entities = [{"text": "Google", "label": "ORG"}]
    
    result = matcher.compare_entities(source_entities, response_entities)
    
    assert result["factual_consistency_score"] == 100.0
    assert len(result["verified"]) == 1
    assert len(result["hallucinated"]) == 0
    # Substring rule maps "Google" vs "Google LLC" to 95.0%
    assert result["verified"][0]["similarity_score"] == 95.0


def test_matcher_hallucination_detection(matcher):
    """Verify that unmatchable entities are flagged as hallucinations."""
    source_entities = [
        {"text": "Apple", "label": "ORG"},
        {"text": "Steve Jobs", "label": "PERSON"}
    ]
    response_entities = [
        {"text": "Apple", "label": "ORG"},
        {"text": "Microsoft", "label": "ORG"} # Hallucinated
    ]
    
    result = matcher.compare_entities(source_entities, response_entities)
    
    assert result["factual_consistency_score"] == 50.0  # 1 out of 2 is hallucinated
    assert len(result["verified"]) == 1
    assert len(result["hallucinated"]) == 1
    assert result["hallucinated"][0]["entity"]["text"] == "Microsoft"


def test_matcher_type_enforcement(matcher):
    """Verify that type matching matches labels properly."""
    source_entities = [{"text": "Paris", "label": "PERSON"}]  # Mislabeled in source for test
    response_entities = [{"text": "Paris", "label": "GPE"}]
    
    # Case 1: type matching is enforced (default)
    result_enforced = matcher.compare_entities(source_entities, response_entities)
    assert result_enforced["factual_consistency_score"] == 0.0
    assert len(result_enforced["hallucinated"]) == 1
    
    # Case 2: type matching is disabled
    matcher_disabled = EntityMatcher(similarity_threshold=80.0, type_matching=False)
    result_disabled = matcher_disabled.compare_entities(source_entities, response_entities)
    assert result_disabled["factual_consistency_score"] == 100.0
    assert len(result_disabled["verified"]) == 1


def test_matcher_empty_cases(matcher):
    """Verify that empty inputs are handled gracefully."""
    # Empty response entities should mean 100% consistency (no hallucinations can be found)
    res = matcher.compare_entities([], [])
    assert res["factual_consistency_score"] == 100.0
    assert res["verified"] == []
    assert res["hallucinated"] == []
