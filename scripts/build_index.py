"""Build the reusable local FAISS index after changing wikipedia.json."""
from __future__ import annotations
import argparse, json, logging, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
PROJECT_ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(PROJECT_ROOT))
from services.config import CURRENT_RETRIEVAL_MODEL, PAPER_RETRIEVAL_MODEL
from services.vector_store import VectorStore, VectorStoreError
KNOWLEDGE_BASE_PATH = PROJECT_ROOT / "knowledge_base" / "wikipedia.json"
def load_documents(path: Path = KNOWLEDGE_BASE_PATH) -> list[dict[str, str]]:
    try: records: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc: raise VectorStoreError(f"Cannot read knowledge base: {path}") from exc
    if not isinstance(records, list) or not records: raise VectorStoreError("wikipedia.json must be a non-empty JSON array.")
    documents = [{"title": r["title"].strip(), "content": r["content"].strip()} for r in records if isinstance(r, dict) and isinstance(r.get("title"), str) and isinstance(r.get("content"), str) and r["title"].strip() and r["content"].strip()]
    if len(documents) != len(records): raise VectorStoreError("Every record requires non-empty string title and content fields.")
    return documents
def build_index(retrieval_mode: str = "current") -> None:
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc: raise VectorStoreError("sentence-transformers is not installed. Run: pip install -r requirements.txt") from exc
    if retrieval_mode not in {"current", "paper"}:
        raise VectorStoreError("retrieval_mode must be 'current' or 'paper'.")
    model_name = CURRENT_RETRIEVAL_MODEL if retrieval_mode == "current" else PAPER_RETRIEVAL_MODEL
    index_name = "vector.index" if retrieval_mode == "current" else "gtr_base.index"
    metadata_name = "metadata.pkl" if retrieval_mode == "current" else "gtr_base_metadata.pkl"
    documents = load_documents(); model = SentenceTransformer(model_name); embeddings = model.encode([d["content"] for d in documents], convert_to_numpy=True, show_progress_bar=True)
    if retrieval_mode == "paper" and embeddings.shape[1] != 768:
        raise VectorStoreError(f"GTR embedding dimension must be 768, got {embeddings.shape[1]}.")
    store = VectorStore(PROJECT_ROOT / "vector_db" / index_name, PROJECT_ROOT / "vector_db" / metadata_name); store.build_index(embeddings, documents); store.save_index()
    if retrieval_mode == "paper":
        manifest = {"model": model_name, "embedding_dimension": int(embeddings.shape[1]), "vector_count": int(embeddings.shape[0]), "metadata_count": len(documents), "index_type": "faiss.IndexFlatIP", "retrieval_mode": "paper", "built_at_utc": datetime.now(timezone.utc).isoformat(), "index_path": str(PROJECT_ROOT / "vector_db" / index_name), "metadata_path": str(PROJECT_ROOT / "vector_db" / metadata_name)}
        (PROJECT_ROOT / "vector_db" / "gtr_base_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build a HaluCheck FAISS index")
    parser.add_argument("--retrieval-mode", choices=("current", "paper"), default="current")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    try: build_index(args.retrieval_mode)
    except VectorStoreError as exc: logging.error("Index build failed: %s", exc); raise SystemExit(1)
