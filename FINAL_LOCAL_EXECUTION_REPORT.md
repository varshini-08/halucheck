# Final Local Execution Report

Validation date: 2026-08-30. Scope: existing `D:\halu` checkout; no benchmark regeneration and no algorithm changes.

| Check | Result | Evidence |
|---|---|---|
| Project entry point | PASS | `app.py` exists |
| Python environment | PASS | Python 3.13.12; `.venv` exists |
| Dependencies | PASS | Streamlit 1.59.2, SentenceTransformers 5.3.0, Transformers 5.3.0, FAISS 1.13.2, pytest 8.4.1, Groq 1.5.0, google-genai 2.19.0 |
| Compilation | PASS | Requested source directories compile cleanly |
| Tests | PASS | `python -m pytest -q tests`: 62 passed, 3 warnings |
| DeBERTa | PASS | `python scripts/test_nli_model.py --offline` loads exact configured model |
| MiniLM | PASS | Cached `all-MiniLM-L6-v2`, 384 dimensions |
| GTR | PASS | Offline model test passes at 768 dimensions |
| FAISS indexes | PASS | MiniLM and GTR indexes, metadata, and GTR manifest exist and validate |
| Streamlit | PASS | Headless startup returned HTTP 200 in the current environment |
| Groq | PASS | One controlled request previously succeeded; key remains local and ignored |
| Gemini | PASS / LIMITED | Connectivity previously succeeded; 10-sample baseline remains quota-limited |
| Security | PASS WITH SCOPE | `.env` ignored; no provider-secret pattern in scanned repository content |

## Current project status

Fully offline: source imports, compilation, unit tests, MiniLM/GTR index validation, GTR smoke, and DeBERTa offline smoke (with caches present). API/internet dependent: Groq/Gemini generation and Wikipedia fallback. Experimental/slow: HaluEval benchmarks, GTR evaluation, comparative runs, and profiling. Not suitable for an unprepared live demo: Gemini baseline, 100-sample benchmark, and any run requiring unavailable quota or network.

## Limitations

Manual browser interaction and screenshots have not been performed in this environment. Gemini’s baseline remains incomplete because of quota exhaustion. SelfCheckNLI requires legitimate multi-response data. Cost analysis is not verified. Paper decomposition and aggregation remain partial/paper-inspired.

Use [MANUAL_LOCAL_EXECUTION_GUIDE.md](docs/MANUAL_LOCAL_EXECUTION_GUIDE.md) for the complete PowerShell procedure.

## React/FastAPI validation update

The preferred local UI is now React on port 5173 with the Vite `/api` proxy
targeting FastAPI on port 8000. FastAPI 0.141.1 and Uvicorn 0.51.0 were
installed into `D:\halu\.venv`; `.venv` imports were verified successfully.
Using a clean validation port, `/api/health`, `/api/history`, `/api/settings`,
and `/docs` all returned HTTP 200. Start both services with
`start_halucheck.bat`; Streamlit remains fallback-only on port 8501.
