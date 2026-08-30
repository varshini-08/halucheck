"""Run the HaluCheck atomic fact extraction demonstration without Streamlit."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from extraction.atomic_fact_extractor import AtomicFactExtractor
from debug.atomic_fact_debug import report_atomic_extraction


def main() -> None:
    question = "Who founded Apple?"
    response = "Apple was founded by Steve Jobs, Steve Wozniak and Ronald Wayne in 1976."
    facts = AtomicFactExtractor().extract_atomic_facts(response)
    report_atomic_extraction(question, response, facts)


if __name__ == "__main__":
    main()
