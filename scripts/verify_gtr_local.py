"""Verify that the complete GTR SentenceTransformer can load without network access."""
from __future__ import annotations
import argparse, json, time
from pathlib import Path

MODEL = "sentence-transformers/gtr-t5-base"

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output")
    args = parser.parse_args()
    started = time.perf_counter()
    result = {"model": MODEL, "network_access_attempted": False, "status": "FAIL"}
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(MODEL, local_files_only=True)
        vectors = model.encode(["offline GTR verification"], convert_to_numpy=True, show_progress_bar=False)
        result.update({"status": "PASS", "embedding_shape": list(vectors.shape), "dimension": int(vectors.shape[1]), "dtype": str(vectors.dtype), "load_seconds": time.perf_counter() - started})
    except Exception as exc:
        result.update({"error": f"{type(exc).__name__}: {exc}", "load_seconds": time.perf_counter() - started})
    print(json.dumps(result, indent=2))
    if args.output: Path(args.output).write_text(json.dumps(result, indent=2), encoding="utf-8")
    return 0 if result["status"] == "PASS" else 1

if __name__ == "__main__": raise SystemExit(main())
