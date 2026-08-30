"""Standalone NLI model smoke test. Run: python scripts/test_nli_model.py"""
from __future__ import annotations

import sys
import traceback
from pathlib import Path
import argparse

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from verification.nli_verifier import NLIVerifier

FACT = "Charles Babbage is the father of the computer."
EVIDENCE = (
    "Charles Babbage was an English mathematician who designed the Analytical "
    "Engine and is often called the father of the computer."
)


def main(offline: bool = False) -> int:
    print("Standalone NLI smoke test started", flush=True)
    try:
        result = NLIVerifier(offline=offline).verify(EVIDENCE, FACT)
    except Exception:
        print("Standalone NLI smoke test failed:", flush=True)
        traceback.print_exc()
        return 1
    print(f"Label: {result.label}")
    print(f"Confidence: {result.confidence:.2%}")
    print(f"Probabilities: {result.probabilities}")
    if result.label != "SUPPORTED" or result.confidence <= 0.90:
        print("Unexpected result: expected SUPPORTED with confidence > 90%.")
        return 2
    print("Standalone NLI smoke test passed.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Require the cached DeBERTa model and make no network request.",
    )
    raise SystemExit(main(parser.parse_args().offline))
