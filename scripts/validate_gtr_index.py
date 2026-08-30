"""Validate the isolated GTR FAISS artifact without rebuilding it."""
from __future__ import annotations

import json
import pickle
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from services.config import PAPER_RETRIEVAL_MODEL
from services.vector_store import VectorStore


def main() -> int:
    index_path = ROOT / "vector_db" / "gtr_base.index"
    metadata_path = ROOT / "vector_db" / "gtr_base_metadata.pkl"
    manifest_path = ROOT / "vector_db" / "gtr_base_manifest.json"
    result: dict[str, object] = {"status": "FAIL", "index": str(index_path), "metadata": str(metadata_path), "manifest": str(manifest_path)}
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        with metadata_path.open("rb") as handle:
            metadata = pickle.load(handle)
        store = VectorStore(index_path, metadata_path)
        store.load_index()
        actual = {"model": manifest.get("model"), "embedding_dimension": store._index.d, "vector_count": store._index.ntotal, "metadata_count": len(metadata), "index_type": type(store._index).__name__, "retrieval_mode": manifest.get("retrieval_mode")}
        checks = {
            "model_is_gtr": actual["model"] == PAPER_RETRIEVAL_MODEL,
            "dimension_is_768": actual["embedding_dimension"] == 768,
            "metadata_matches_vectors": actual["vector_count"] == actual["metadata_count"],
            "manifest_vector_count_matches": manifest.get("vector_count") == actual["vector_count"],
            "manifest_metadata_count_matches": manifest.get("metadata_count") == actual["metadata_count"],
            "manifest_dimension_matches": manifest.get("embedding_dimension") == actual["embedding_dimension"],
            "paper_mode": actual["retrieval_mode"] == "paper",
            "separate_from_minilm": index_path.name == "gtr_base.index" and index_path.name != "vector.index",
        }
        result.update({"actual": actual, "manifest_values": manifest, "checks": checks, "status": "PASS" if all(checks.values()) else "FAIL"})
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    destination = ROOT / "results" / "final_validation"
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "gtr_index_validation.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    lines = ["# GTR Index Validation", "", f"- Status: {result['status']}"]
    for name, value in result.get("checks", {}).items():
        lines.append(f"- {name}: {value}")
    if result.get("error"):
        lines.append(f"- Error: {result['error']}")
    (destination / "gtr_index_validation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
