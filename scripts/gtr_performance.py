"""Measure the available local GTR retrieval stages without estimating NLI."""
from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter

from services.retriever import EvidenceRetriever


def main() -> int:
    query = "Paris is the capital of France."
    retriever = EvidenceRetriever(retrieval_mode="paper", offline=True, enable_wikipedia_fallback=False)
    started = perf_counter(); retriever._get_embedder(); model_load = perf_counter() - started
    started = perf_counter(); embedding = retriever._embedding_for(query); embedding_time = perf_counter() - started
    retriever.store.load_index()
    started = perf_counter(); retriever.store.search(embedding, 2); faiss_time = perf_counter() - started
    started = perf_counter(); result = retriever.retrieve(query, 2); total = perf_counter() - started
    payload = {"model": retriever.model_name, "retrieval_mode": "paper/GTR", "embedding_dimension": int(retriever.store._index.d), "query": query, "model_load_seconds": model_load, "embedding_seconds": embedding_time, "faiss_retrieval_seconds": faiss_time, "total_retrieval_seconds": total, "full_verification_seconds": None, "result_count": len(result.retrieved_evidence), "offline": True}
    destination = Path("results/performance"); destination.mkdir(parents=True, exist_ok=True)
    (destination / "gtr_performance.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (destination / "gtr_performance.md").write_text("# GTR Performance\n\n" + "\n".join(f"- {key}: {value}" for key, value in payload.items()) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
