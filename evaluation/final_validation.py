"""Deterministic, non-destructive validation artifacts for the project."""
from __future__ import annotations
import json, time
from pathlib import Path
from extraction.atomic_fact_extractor import AtomicFactExtractor
from .halu_eval_loader import load_halueval

ROOT = Path(__file__).resolve().parents[1]

def validate_phase1(output: Path) -> dict:
    extractor = AtomicFactExtractor()
    cases = {
        "simple": "Paris is the capital of France.",
        "objects": "A table held a book and a vase of fresh-cut flowers.",
        "dates_numbers": "Ada Lovelace wrote notes in 1843.",
        "entities": "Apple was founded by Steve Jobs.",
        "numbered": "1. Mercury is a planet.\n2. Venus is a planet.",
        "modifiers": "A cream leather sofa stood beside a mahogany bookcase.",
        "empty": "",
    }
    results = {}
    for name, text in cases.items():
        started = time.perf_counter()
        facts = extractor.extract_atomic_facts(text)
        results[name] = {"fact_count": len(facts), "facts": [f.fact_text for f in facts], "seconds": time.perf_counter() - started}
    output.mkdir(parents=True, exist_ok=True)
    (output / "phase1_validation.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    (output / "phase1_validation.md").write_text("# Phase 1 Validation\n\n" + "\n".join(f"- **{k}**: {v['fact_count']} fact(s)" for k, v in results.items()) + "\n", encoding="utf-8")
    return results

def validate_dataset(path: Path, output: Path) -> dict:
    samples = load_halueval(str(path))
    result = {"path": str(path), "records": len(samples), "labels": {"hallucination": sum(s.hallucination for s in samples), "no_hallucination": sum(not s.hallucination for s in samples)}}
    output.mkdir(parents=True, exist_ok=True)
    (output / "dataset_validation.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result

if __name__ == "__main__":
    out = ROOT / "results" / "final_validation"
    print(json.dumps({"phase1": validate_phase1(out), "dataset": validate_dataset(ROOT / "data" / "halu_eval" / "general_data.json", out)}, indent=2))
