# HaluCheck Academic Submission Package

## Title

HaluCheck — Explainable Hallucination Detection

## Problem and objectives

LLM answers can sound authoritative while containing unsupported statements. HaluCheck generates an answer, decomposes it into checkable claims, retrieves source evidence, applies NLI, and explains the result. Objectives are traceability, source-aware verification, transparent metrics, and persistent review.

## Architecture and technologies

React/Vite frontend; FastAPI backend; Groq/Gemini providers; FAISS/MiniLM local retrieval; Wikipedia and optional source adapters; cached/batched DeBERTa-v3 MNLI; SQLite history.

## Workflow and algorithms

Question → LLM answer → atomic claim extraction/filtering → domain routing → evidence retrieval → normalization/deduplication/relevance filtering → NLI → Supported/Contradicted/Neutral → metrics/history/export.

Hallucination rate is contradicted/total; support rate is supported/total; neutral rate is neutral/total; evidence coverage is claims with evidence/total. Neutral is unverified, not hallucinated.

## Results and testing

Validated reports record 70 passing tests and one skipped test, successful Python compilation, React production build, API smoke checks, security checks, and live Groq analysis. A measured Earth-question run completed in approximately 18–19 seconds with four claims. Timing varies by warm-up, hardware, indexes, and network sources.

## Evidence and security

Use `FINAL_EVIDENCE_INDEX.md` and `FINAL_SCREENSHOT_CHECKLIST.md` for manual proof. API keys remain backend-only in `.env`; optional sources are not claimed active unless configured and returning evidence.

## How to run and demonstrate

```powershell
cd D:\halu
.\start_halucheck.bat
```

Open `http://localhost:5173`, run a factual question, inspect claims/evidence, expand an evidence accordion, review metrics/history, and export the report. Use `FINAL_DEMO_SCRIPT.md` and `DEMO_TEST_CASES.md`.

## Limitations and future scope

Browser screenshots, responsive inspection, Gemini quota testing, and configured optional-source benchmarks require manual execution. Future work includes broader datasets, authoritative adapters, and controlled cold/warm benchmarking.
