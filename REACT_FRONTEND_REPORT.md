# HaluCheck React frontend implementation report

## Result

HaluCheck now has a standalone React + TypeScript + Vite frontend in
`frontend/`. The existing Streamlit application remains available as a
fallback. The React UI is not rendered inside Streamlit.

## Architecture

- `frontend/src/App.tsx`: dashboard, analysis form, metrics, claims, evidence,
  history summary, error/loading states, and real JSON report download.
- `frontend/src/styles.css`: dark responsive SaaS dashboard styling.
- `api/main.py`: thin FastAPI adapter that calls the existing LLM providers and
  `HaluCheckPipeline`; it does not duplicate research logic.
- Vite proxies `/api` to `http://127.0.0.1:8000`.

The backend research algorithms, retrieval, extraction, NLI, evaluation,
datasets, indexes, and existing tests were not rewritten.

## Endpoints

- `GET /api/health`
- `GET /api/config`
- `GET /api/settings`
- `POST /api/analyze`
- `POST /api/regenerate`
- `GET /api/history`
- `GET /api/dashboard`
- `GET /api/report/{analysis_id}`

Analysis values, claims, evidence, confidence, processing time, and history are
serialized from actual pipeline results. No sample dashboard data is inserted.

## Validation

```powershell
cd D:\halu
python -m py_compile app.py api\main.py
python -m pytest -q tests

cd frontend
npm install
npm run build
```

Results: npm install completed with zero vulnerabilities; Vite `8.2.2`
production build passed; Python test suite passed (`62 passed`, 3 existing
deprecation warnings). FastAPI returned HTTP 200 for `/api/health` and
`/api/config`. The new `/api/settings`, `/api/history`, `/api/dashboard`, and
`/docs` endpoints also returned HTTP 200 during clean-port validation. Vite development server
returned HTTP 200 on port 5173. Port 8000 was briefly occupied by a stale
process during one check; the API was confirmed on clean port 8010 and the
documented startup port remains 8000.

## Run locally

Terminal 1:

```powershell
cd D:\halu
python -m uvicorn api.main:app --reload --port 8000
```

Terminal 2:

```powershell
cd D:\halu\frontend
npm run dev
```

Open `http://localhost:5173`. API keys remain backend environment variables;
do not place them in React source code.

## Manual browser checks

The standalone page was server-validated at `http://127.0.0.1:5173` and the
API at `http://127.0.0.1:8000`. Browser-level clicking and visual inspection
must still be performed in the user's browser. Verify provider switching,
question submission, real analysis output, claims/evidence, export, responsive
layout, and error states there.

## Known limitations

- History is process-memory only; persistence can be added later without
  changing the UI contract.
- The first analysis may take time while local retrieval/NLI models load.
- The API intentionally does not expose API keys to the browser.

The frontend API client safely handles connection failures, empty bodies,
invalid JSON, and FastAPI error payloads, preventing the previous
`Unexpected end of JSON input` message from masking the real backend error.

Evidence is now rendered as independently collapsible accordions. Collapsed
items show a two-line preview; expanded evidence is capped at 360px with an
internal scrollbar, keeping Verification Details and the dashboard visible
without hiding or fabricating backend evidence.

## Combined Windows startup

Run `D:\halu\start_halucheck.bat` to launch separate backend and frontend
terminals. The backend entrypoint is `api.main:app` on port 8000 and the Vite
proxy targets `http://127.0.0.1:8000`.
