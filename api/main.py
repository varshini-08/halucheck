"""Thin REST adapter over the existing HaluCheck services."""
from datetime import datetime, timezone
from functools import lru_cache
import os
from time import perf_counter
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.analysis_service import HaluCheckPipeline, AnalysisResult
from services.llm_service import GroqProvider, LLMServiceException
from services.gemini_service import GeminiProvider
from verification.verification_pipeline import VerificationPipeline
from sources.registry import source_catalog

app = FastAPI(title="HaluCheck API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_methods=["*"], allow_headers=["*"])
HISTORY: list[dict] = []

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
    payload = {"id": str(len(HISTORY) + 1), "question": question, "response": result.response, "claims": claims, "provider": provider, "model": _model(provider), "verification_engine": "DeBERTa-v3 MNLI", "timestamp": datetime.now(timezone.utc).isoformat(), "processing_time": elapsed, "retrieval_mode": result.comparison.get("retrieval_mode", "Unknown"), "evidence_sources": result.comparison.get("evidence_count", 0), "metrics": {"hallucination_score": sum(c["hallucination"] for c in claims) / len(result.facts) if result.facts else 0, "claims_analyzed": len(result.facts), "supported": supported, "contradicted": contradicted, "neutral": neutral}}
    return payload

@app.get("/api/health")
def health(): return {"status": "ok", "service": "HaluCheck API"}

@app.get("/api/config")
def config(): return {"providers": ["groq", "gemini"], "models": {"groq": _model("groq"), "gemini": _model("gemini")}}

@app.get("/api/settings")
def settings(): return config()

@app.get("/api/sources")
def sources(): return source_catalog()

@app.get("/api/sources/status")
def source_status(): return {item["name"]: item["status"] for item in source_catalog()}

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
        started = perf_counter(); response = llm.generate_response(question)
        result = pipeline().analyse(response, question=question)
        payload = _serialize(result, question, provider, perf_counter() - started); HISTORY.append(payload); return payload
    except (LLMServiceException, Exception) as exc:
        raise HTTPException(502, str(exc)) from exc

@app.post("/api/regenerate")
def regenerate(request: AnalyzeRequest):
    return analyze(request)

@app.get("/api/report/{analysis_id}")
def report(analysis_id: str):
    for item in HISTORY:
        if item["id"] == analysis_id:
            return item
    raise HTTPException(404, "Analysis report not found.")
