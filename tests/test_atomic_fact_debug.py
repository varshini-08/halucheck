from debug.atomic_fact_debug import build_debug_report
from extraction.atomic_fact_extractor import AtomicFactExtractor


def test_debug_report_includes_pipeline_sections():
    facts = AtomicFactExtractor().extract_atomic_facts("Apple was founded by Steve Jobs.")
    report = build_debug_report("Who founded Apple?", "Apple was founded by Steve Jobs.", facts)

    for heading in [
        "QUESTION",
        "LLM RESPONSE",
        "SENTENCE SPLITTING",
        "ATOMIC FACTS",
        "ENTITY DETECTION",
        "SUMMARY",
        "Status : Extraction Successful",
    ]:
        assert heading in report
