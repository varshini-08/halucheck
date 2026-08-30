from extraction.atomic_fact_extractor import AtomicFactExtractor
from services.analysis_service import HaluCheckPipeline


def test_atomic_fact_extractor_creates_fact_records_with_entities():
    facts = AtomicFactExtractor().extract_atomic_facts(
        "Apple was founded by Steve Jobs. Apple was founded by Steve Wozniak."
    )

    assert [fact.fact_id for fact in facts] == ["fact-1", "fact-2"]
    assert facts[0].fact_text == "Apple was founded by Steve Jobs."
    assert {entity["text"] for entity in facts[0].entities} == {"Apple", "Steve Jobs"}


def test_pipeline_matches_repeated_entities_and_marks_uncorroborated_ones():
    result = HaluCheckPipeline().analyse(
        "Apple was founded by Steve Jobs. Apple was founded by Steve Wozniak."
    )

    assert result.comparison["total_facts"] == 2
    assert result.comparison["total"] == 4
    assert len(result.comparison["matched"]) == 2
    assert len(result.comparison["hallucinated"]) == 2


def test_person_list_is_split_into_person_and_date_facts():
    facts = AtomicFactExtractor().extract_atomic_facts(
        "Apple was founded by Steve Jobs, Steve Wozniak and Ronald Wayne in 1976."
    )

    assert [fact.fact_text for fact in facts] == [
        "Apple was founded by Steve Jobs.",
        "Apple was founded by Steve Wozniak.",
        "Apple was founded by Ronald Wayne.",
        "Apple was founded in 1976.",
    ]
    assert sum(len(fact.entities) for fact in facts) == 7


def test_atomic_facts_reject_fragments_and_merge_duplicate_variants():
    extractor = AtomicFactExtractor()

    assert extractor._is_complete_fact("and in 1976.") is False
    facts = extractor.extract_atomic_facts(
        "Ada Lovelace wrote notes in 1843. Ada Lovelace wrote notes in 1843."
    )

    assert [fact.fact_text for fact in facts] == ["Ada Lovelace wrote notes in 1843."]


def test_atomic_facts_are_capped_for_dashboard_presentation():
    extractor = AtomicFactExtractor()
    text = " ".join(f"Ada wrote book {number}." for number in range(12))

    assert len(extractor.extract_atomic_facts(text)) == 10

def test_coordination_preserves_objects_and_subjects():
    facts = AtomicFactExtractor().extract_atomic_facts(
        "In the center of the room, a low coffee table held a collection of art books and a vase of fresh-cut flowers. A plush wool rug lay beneath the furniture, and a collection of framed artwork adorned the walls, completing the roomâ€™s air of elegance and comfort."
    )
    texts = [fact.fact_text for fact in facts]
    assert "a low coffee table held a collection of art books." in texts
    assert "a low coffee table held a vase of fresh-cut flowers." in texts
    assert all("a a" not in text.lower() for text in texts)
    assert any("framed artwork adorned the walls" in text.lower() for text in texts)
    assert not any("rug adorned the walls" in text.lower() for text in texts)


def test_numbered_list_items_do_not_merge_into_malformed_facts():
    facts = AtomicFactExtractor().extract_atomic_facts(
        "1. The student wakes up at a reasonable time.\n"
        "2. The student brushes teeth before breakfast.\n"
        "3. The student makes the bed."
    )

    assert [fact.fact_text for fact in facts] == [
        "The student wakes up at a reasonable time.",
        "The student brushes teeth before breakfast.",
        "The student makes the bed.",
    ]


def test_markdown_table_rows_do_not_become_table_fragments():
    facts = AtomicFactExtractor().extract_atomic_facts(
        "| What | Who / How |\n"
        "|------|-----------|\n"
        "| Legislative creation | The U.S. Congress passed the Act in 1958. |"
    )

    assert len(facts) == 1
    assert "------" not in facts[0].fact_text
    assert "The U.S. Congress passed the Act in 1958." in facts[0].fact_text

