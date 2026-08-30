"""Explicit GTR smoke test; never falls back to the production MiniLM model."""
from __future__ import annotations
import argparse, json, time
from pathlib import Path

MODEL = "sentence-transformers/gtr-t5-base"

def smoke(offline: bool = False):
    started = time.perf_counter()
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(MODEL, local_files_only=offline)
    vectors = model.encode(["The Eiffel Tower is in Paris.", "Paris is the capital of France."], convert_to_numpy=True, show_progress_bar=False)
    if vectors.ndim != 2 or vectors.shape[1] != 768:
        raise RuntimeError(f"Expected GTR dimension 768, got {vectors.shape}")
    result = {"model": MODEL, "embedding_shape": list(vectors.shape), "dtype": str(vectors.dtype), "dimension": int(vectors.shape[1]), "seconds": time.perf_counter() - started, "status": "PASS"}
    print(json.dumps(result, indent=2)); return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--output"); parser.add_argument("--offline", action="store_true"); args = parser.parse_args()
    try: result = smoke(args.offline)
    except Exception as exc:
        result = {"model": MODEL, "status": "FAIL", "error": type(exc).__name__ + ": " + str(exc)}; print(json.dumps(result, indent=2)); raise SystemExit(1)
    if args.output: Path(args.output).write_text(json.dumps(result, indent=2), encoding="utf-8")
