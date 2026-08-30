"""Measure one supplied response through the existing pipeline.

This profiler never generates a new LLM response. Pass a response explicitly or
select one from HaluEval; timings are measured from the current run only.
"""
from __future__ import annotations
import argparse, json, time
from pathlib import Path
from services.analysis_service import HaluCheckPipeline
from verification.verification_pipeline import VerificationPipeline
from .halu_eval_loader import load_halueval

def profile(response: str, question: str = "", output: str | Path | None = None, pipeline=None):
    pipeline = pipeline or HaluCheckPipeline(verification_pipeline=VerificationPipeline())
    started = time.perf_counter(); result = pipeline.analyse(response, question=question); total = time.perf_counter() - started
    retrieval = getattr(pipeline.retriever, "last_timings", {})
    stages = {
        "extraction_and_entities_seconds": None,
        "embedding_seconds": None,
        "local_faiss_seconds": retrieval.get("local_faiss_seconds", 0.0),
        "wikipedia_search_seconds": retrieval.get("wikipedia_search_seconds", 0.0),
        "wikipedia_article_seconds": retrieval.get("wikipedia_article_seconds", 0.0),
        "wikipedia_chunk_ranking_seconds": retrieval.get("wikipedia_chunk_ranking_seconds", 0.0),
        "nli_seconds": None,
        "classification_seconds": None,
        "total_seconds": total,
    }
    report = {"question": question, "fact_count": len(result.facts), "entity_count": sum(len(f.entities) for f in result.facts), "evidence_count": sum(len(r.retrieved_evidence) for r in result.retrievals), "predicted_label": "hallucination" if any(v.hallucination for v in result.verifications) else "no_hallucination", "stages": stages, "cache_hits": getattr(pipeline.retriever, "cache_hits", 0), "cache_misses": getattr(pipeline.retriever, "cache_misses", 0), "note": "Unset stage values are not instrumented separately in the existing production pipeline; no timings are estimated."}
    if output: Path(output).write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--response"); parser.add_argument("--dataset"); parser.add_argument("--sample-index",type=int,default=0); parser.add_argument("--question",default=""); parser.add_argument("--output",default="results/performance/profile.json"); args=parser.parse_args()
    response=args.response; question=args.question
    if not response and args.dataset:
        sample=list(load_halueval(args.dataset))[args.sample_index]; response=sample.response; question=sample.query
    if not response: parser.error("provide --response or --dataset")
    print(json.dumps(profile(response,question,args.output),indent=2))
if __name__ == "__main__": main()
