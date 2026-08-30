"""Thin REST adapter over the existing HaluCheck services."""
from datetime import datetime, timezone
from functools import lru_cache
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import perf_counter
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.analysis_service import HaluCheckPipeline, AnalysisResult
from services.llm_service import GroqProvider, LLMServiceException
from services.gemini_service import GeminiProvider
from verification.verification_pipeline import VerificationPipeline
from sources.registry import source_catalog
from api.storage import load_all, save
from sources.adapters import ADAPTERS
from sources.routing import route_claim, deduplicate_evidence
from services.retriever import FactRetrieval
from services.vector_store import Evidence

app = FastAPI(title="HaluCheck API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_methods=["*"], allow_headers=["*"])
HISTORY: list[dict] = load_all()

class AnalyzeRequest(BaseModel):
    question: str
    provider: str = "groq"
    model: str | None = None
    retrieval: dict | None = None
    verification_engine: str | None = None

@lru_cache(maxsize=1)
def pipeline() -> HaluCheckPipeline:
    return HaluCheckPipeline(verification_pipeline=VerificationPipeline())

def _model(provider: str) -> str:
    return os.getenv("GEMINI_MODEL", "gemini-3.6-flash") if provider == "gemini" else os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

def _serialize(result: AnalysisResult, question: str, provider: str, elapsed: float) -> dict:
    claims = []
    for item in result.verifications:
        evidence = []
        for ev in item.evidence_verifications:
            evidence.append({"content": ev.evidence.content, "source": ev.evidence.source, "title": ev.evidence.title, "url": ev.evidence.url, "similarity": ev.evidence.score, "confidence": ev.result.confidence})
        claims.append({"fact": item.fact, "label": item.label, "confidence": item.confidence, "hallucination": item.hallucination, "reason": item.reason, "evidence": evidence})
    supported = sum(c["label"] == "SUPPORTED" for c in claims)
    contradicted = sum(c["label"] == "CONTRADICTED" for c in claims)
    neutral = sum(c["label"] == "NEUTRAL" for c in claims)
    total = len(result.facts)
    payload = {"id": str(len(HISTORY) + 1), "question": question, "response": result.response, "claims": claims, "provider": provider, "model": _model(provider), "verification_engine": "DeBERTa-v3 MNLI", "timestamp": datetime.now(timezone.utc).isoformat(), "processing_time": elapsed, "retrieval_mode": result.comparison.get("retrieval_mode", "Unknown"), "evidence_sources": result.comparison.get("evidence_count", 0), "metrics": {"hallucination_score": sum(c["hallucination"] for c in claims) / total if total else 0, "claims_analyzed": total, "supported": supported, "contradicted": contradicted, "neutral": neutral, "hallucination_rate": contradicted / total if total else 0, "support_rate": supported / total if total else 0, "neutral_rate": neutral / total if total else 0, "evidence_coverage": sum(bool(c["evidence"]) for c in claims) / total if total else 0}}
    return payload

def _enrich_with_external_sources(result: AnalysisResult) -> AnalysisResult:
    """Query routed adapters concurrently and re-use the existing NLI rules."""
    jobs = []
    for fact in result.facts:
        claim = fact.fact_text
        for source_id in route_claim(claim):
            adapter = ADAPTERS.get(source_id)
            if adapter and adapter.is_configured(): jobs.append((fact, source_id, adapter))
    if not jobs: return result
    grouped: dict[str, list[dict]] = {}
    with ThreadPoolExecutor(max_workers=min(6, len(jobs))) as pool:
        futures = {pool.submit(adapter.search, fact.fact_text): (fact, source_id) for fact, source_id, adapter in jobs}
        for future in as_completed(futures):
            fact, source_id = futures[future]
            try:
                for item in future.result()[:3]:
                    if item.content:
                        grouped.setdefault(fact.fact_text, []).append({"title": item.title, "content": item.content, "url": item.url, "source": source_id})
            except Exception:
                continue
    if not grouped: return result
    retrieval_map = {item.fact: item for item in result.retrievals}
    enriched = []
    for fact in result.facts:
        existing = retrieval_map.get(fact.fact_text)
        base = [{"title": x.title, "content": x.content, "url": x.url, "source": x.source} for x in (existing.retrieved_evidence if existing else [])]
        merged = deduplicate_evidence(base + grouped.get(fact.fact_text, []))
        evidence = [Evidence(x.get("title") or x.get("source", "Evidence"), x.get("content", ""), .5, i + 1, x.get("source", "external"), x.get("url")) for i, x in enumerate(merged)]
        enriched.append(FactRetrieval(fact.fact_text, evidence, existing.used_wikipedia_fallback if existing else False, existing.local_average_similarity if existing else 0.0))
    result.retrievals = enriched
    result.verifications = result.comparison.get("verification_pipeline").verify_many(enriched) if result.comparison.get("verification_pipeline") else result.verifications
    return result

@app.get("/api/health")
def health(): return {"status": "ok", "service": "HaluCheck API"}

@app.get("/api/config")
def config(): return {"providers": ["groq", "gemini"], "models": {"groq": _model("groq"), "gemini": _model("gemini")}}

@app.get("/api/provider/status")
def provider_status(provider: str = "groq"):
    provider = provider.lower().strip()
    if provider not in {"groq", "gemini"}:
        raise HTTPException(400, "Unsupported provider.")
    configured = bool(os.getenv("GEMINI_API_KEY" if provider == "gemini" else "GROQ_API_KEY", "").strip())
    return {"provider": provider, "model": _model(provider), "status": "configured" if configured else "not_configured", "configured": configured}

@app.get("/api/settings")
def settings(): return config()

@app.get("/api/sources")
def sources(): return source_catalog()

@app.get("/api/sources/status")
def source_status(): return {item["name"]: item["status"] for item in source_catalog()}

@app.get("/api/sources/{source_id}/search")
def source_search(source_id: str, claim: str):
    adapter = ADAPTERS.get(source_id)
    if not adapter: raise HTTPException(404, "Source adapter is not available.")
    if not adapter.is_configured(): raise HTTPException(503, "Source is not configured.")
    try:
        return [item.__dict__ for item in adapter.search(claim)]
    except Exception:
        raise HTTPException(502, "Source unavailable; continuing with other sources.")

@app.get("/api/history")
def history(): return HISTORY

@app.get("/api/dashboard")
def dashboard():
    total = sum(int(x["metrics"]["claims_analyzed"]) for x in HISTORY)
    supported = sum(int(x["metrics"]["supported"]) for x in HISTORY)
    return {"total_analyses": len(HISTORY), "avg_hallucination_score": sum(x["metrics"]["hallucination_score"] for x in HISTORY) / len(HISTORY) if HISTORY else 0, "accuracy": supported / total if total else 0, "avg_response_time": sum(x["processing_time"] for x in HISTORY) / len(HISTORY) if HISTORY else 0, "history": HISTORY}

@app.post("/api/analyze")
def analyze(request: AnalyzeRequest):
    question = request.question.strip(); provider = request.provider.lower().strip()
    if not question: raise HTTPException(400, "Please provide a question.")
    if provider not in {"groq", "gemini"}: raise HTTPException(400, "Unsupported provider.")
    key = os.getenv("GEMINI_API_KEY" if provider == "gemini" else "GROQ_API_KEY", "").strip()
    if not key: raise HTTPException(503, f"{provider.title()} API key is not configured.")
    try:
        llm = GeminiProvider(key, _model(provider)) if provider == "gemini" else GroqProvider(key, _model(provider))
        started = perf_counter(); llm_started = perf_counter(); response = llm.generate_response(question); llm_seconds = perf_counter() - llm_started
        result = pipeline().analyse(response, question=question)
        # Re-run the existing verifier over local plus routed external evidence.
        result.comparison["verification_pipeline"] = pipeline().verification_pipeline
        result = _enrich_with_external_sources(result)
        result.comparison.pop("verification_pipeline", None)
        payload = _serialize(result, question, provider, perf_counter() - started)
        payload["timing"] = {**result.comparison.get("timings", {}), "llm_seconds": llm_seconds}
        storage_started = perf_counter(); HISTORY.insert(0, payload); save(payload); payload["timing"]["storage_seconds"] = perf_counter() - storage_started
        return payload
    except LLMServiceException as exc:
        raise HTTPException(exc.status_code, {"provider": provider, "error_type": exc.error_type, "message": str(exc)}) from exc
    except Exception as exc:
        raise HTTPException(500, {"provider": provider, "error_type": "internal_error", "message": "Analysis failed. Check backend logs."}) from exc

@app.post("/api/regenerate")
def regenerate(request: AnalyzeRequest):
    return analyze(request)

@app.get("/api/report/{analysis_id}")
def report(analysis_id: str):
    for item in HISTORY:
        if item["id"] == analysis_id:
            return item
    raise HTTPException(404, "Analysis report not found.")
