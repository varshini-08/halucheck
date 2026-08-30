# End-to-end validation report

## Results

| Area | Result | Evidence |
|---|---|---|
| Project environment | PASS | Python 3.13.12, FastAPI 0.141.1, Uvicorn 0.51.0, Node 22.17.0, npm 10.9.2 |
| Python compilation | PASS | `compileall` exit 0 |
| Regression tests | PASS | 68 tests passed, 3 existing deprecation warnings |
| React production build | PASS | Vite 8.2.2 build completed |
| FastAPI startup | PASS | `api.main:app` started successfully |
| React startup | PASS | Vite returned HTTP 200 on port 5173 |
| API endpoints | PASS | health/config/settings/history/sources/status/dashboard/docs all HTTP 200 |
| Security | PASS | `.env` ignored; no frontend secrets; node_modules excluded |
| Browser visual testing | NOT TESTED | Requires manual browser inspection |
| Real provider analysis | NOT TESTED | Not repeated to avoid consuming provider quota |

## Active/live behavior

Local FAISS and Wikipedia are the existing production retrieval adapters. The
new Wikidata, World Bank, PubMed, Crossref, OpenAlex, and Google Fact Check
adapters have official API implementations and are routed when configured;
their live external calls were not represented as PASS without a dedicated
network/API run. Google Fact Check requires `GOOGLE_FACT_CHECK_API_KEY`.

Government, UN Data, WHO, NASA, NOAA, Britannica, and Reuters/AP are marked
unavailable, not configured, or access-dependent rather than presented as
active evidence sources.

## Failure isolation and persistence

External adapter exceptions are caught per source and do not abort analysis.
Completed API analyses are stored in SQLite at
`results/halucheck_history.sqlite3`, and `/api/history` reloads them after a
backend restart.

## Reproduce

```powershell
cd D:\halu
.\.venv\Scripts\Activate.ps1
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

In another terminal:

```powershell
cd D:\halu\frontend
npm run dev
```

Open `http://localhost:5173` and manually test the question flow, accordion
evidence, history persistence, export, and responsive layout.
