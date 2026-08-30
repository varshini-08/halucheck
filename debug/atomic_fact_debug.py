"""Console and file reporting for atomic fact extraction demonstrations."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable

from extraction.atomic_fact_extractor import AtomicFact


OUTPUT_FILE = Path(__file__).resolve().parents[1] / "outputs" / "atomic_fact_output.txt"
DIVIDER = "=" * 58


def build_debug_report(question: str, response: str, facts: Iterable[AtomicFact]) -> str:
    """Build the structured, human-readable extraction report."""
    fact_list = list(facts)
    sentences = list(dict.fromkeys(fact.source_sentence for fact in fact_list))
    lines = [
        DIVIDER,
        f"Atomic Fact Extraction Debug | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        DIVIDER,
        "\nQUESTION",
        question or "(not provided)",
        "\nLLM RESPONSE",
        response,
        "\nSENTENCE SPLITTING",
    ]
    lines.extend(f"Sentence {index}: {sentence}" for index, sentence in enumerate(sentences, 1))
    lines.append("\nATOMIC FACTS")
    lines.extend(
        f"Fact {index}: {fact.fact_text}" for index, fact in enumerate(fact_list, 1)
    )
    lines.append("\nENTITY DETECTION")
    for index, fact in enumerate(fact_list, 1):
        lines.append(f"Fact {index}")
        if fact.entities:
            lines.extend(f"  {entity['text']} ({entity['label']})" for entity in fact.entities)
        else:
            lines.append("  No supported entities detected")

    entity_count = sum(len(fact.entities) for fact in fact_list)
    status = "Extraction Successful" if fact_list else "No Atomic Facts Extracted"
    lines.extend([
        "\nSUMMARY",
        "Question Processed Successfully" if fact_list else "Question Processed Without Atomic Facts",
        f"Atomic Facts : {len(fact_list)}",
        f"Entities : {entity_count}",
        f"Status : {status}",
        DIVIDER,
    ])
    return "\n".join(lines)


def report_atomic_extraction(question: str, response: str, facts: Iterable[AtomicFact]) -> None:
    """Print the report and append it to the timestamped development log."""
    report = build_debug_report(question, response, facts)
    print(report, flush=True)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("a", encoding="utf-8") as output:
        output.write(report + "\n\n")
