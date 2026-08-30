# HaluCheck Manual Local Execution Guide

This guide runs the existing project at `D:\halu`. It does not clone, pull, regenerate indexes, or change algorithms.

## 1. Start and environment

```powershell
cd D:\halu
python --version
Test-Path .venv\Scripts\Activate.ps1
.\.venv\Scripts\Activate.ps1
python -m pip --version
```

The current workspace has Python 3.13.12 and an existing `.venv`. If a fresh environment is genuinely required:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Verify installed packages without secrets:

```powershell
python -c "import importlib.metadata as m; names=['streamlit','sentence-transformers','transformers','faiss-cpu','pytest','groq','google-genai']; print({p:(m.version(p) if any(d.metadata['Name'].lower()==p.lower() for d in m.distributions()) else 'MISSING') for p in names})"
```

## 2. Configure providers

```powershell
Copy-Item .env.example .env -ErrorAction SilentlyContinue
notepad .env
```

Use placeholders in documentation only:

```text
GROQ_API_KEY=YOUR_GROQ_KEY
GROQ_MODEL=openai/gpt-oss-20b
GEMINI_API_KEY=YOUR_GEMINI_KEY
GEMINI_MODEL=gemini-3.6-flash
LLM_PROVIDER=groq
```

Set `LLM_PROVIDER=gemini` to use Gemini, or select the provider in the Streamlit sidebar. Check configuration without printing values:

```powershell
python -c "from utils.env_utils import load_environment; load_environment(); import os; print('Groq configured:', bool(os.getenv('GROQ_API_KEY'))); print('Gemini configured:', bool(os.getenv('GEMINI_API_KEY'))); print('Provider:', os.getenv('LLM_PROVIDER','groq'))"
```

## 3. Verify models

```powershell
python -c "from sentence_transformers import SentenceTransformer; m=SentenceTransformer('all-MiniLM-L6-v2', local_files_only=True); print('MiniLM dimension:', m.encode(['offline check'], convert_to_numpy=True, show_progress_bar=False).shape[1])"
python scripts/test_nli_model.py --offline
python scripts/verify_gtr_local.py
python scripts/test_gtr.py --offline
```

The configured models are MiniLM (384d), DeBERTa-v3 MNLI, and GTR-T5-base (768d). Offline commands require their local Hugging Face caches.

## 4. Verify indexes

```powershell
python scripts/validate_gtr_index.py
```

Production mode uses `all-MiniLM-L6-v2` → `vector_db/vector.index` and `vector_db/metadata.pkl` (384d). Paper mode uses `sentence-transformers/gtr-t5-base` → `vector_db/gtr_base.index`, `gtr_base_metadata.pkl`, and `gtr_base_manifest.json` (768d). Rebuild only if missing:

```powershell
python scripts/build_index.py
python scripts/build_index.py --retrieval-mode paper
```

The paper command writes only the GTR-named artifacts; it does not replace the production index.

## 5. Start Streamlit

```powershell
cd D:\halu
python -m streamlit run app.py
```

Open `http://localhost:8501`. If occupied, use `python -m streamlit run app.py --server.port 8502`. Stop with `Ctrl+C`. Use `python -m streamlit` if the `streamlit` executable is not on PATH.

## 6. Manual UI tests

Enter a question in the UI; HaluCheck generates the response through the selected provider, extracts facts, retrieves evidence, and renders labels. Record actual observations; do not mark these as passed until manually performed.

| Case | Question | Expected observation |
|---|---|---|
| Normal factual | Who created Python? | Response and supported/evidence facts appear |
| Hallucinated | Who created Python in 1600? | Contradicted or neutral claims are highlighted |
| Mixed | When was NASA founded and who founded it? | Multiple facts can have different labels |
| Entity | Where is the Eiffel Tower? | Entity evidence and source are shown |
| Date/number | When was NASA founded? | Date claim is checked against evidence |
| Retrieval | What is FAISS used for? | Local evidence cards appear |
| Wikipedia fallback | Ask about a topic absent from the local KB | Fallback may appear if network is available |
| No evidence | Describe an imaginary moon named Zephyria | Neutral/no-useful-evidence state is shown |
| Empty input | Submit with no question | Verify button remains disabled or a safe error appears |
| Provider | Select Groq, then Gemini | Selected provider/model and key status update |

Also check conversation history, regenerate, timing, hallucination percentage, severity, evidence count, and Developer Details expansion. Screenshots require a real browser and must have keys obscured.

## 7. Provider and benchmark commands

```powershell
python scripts/test_gemini.py
python test_groq.py
python -m evaluation.baseline_runner --baseline llm --provider gemini --dataset data/halu_eval/general_data.json --samples 10 --seed 42
```

The Gemini baseline requires quota and 10 successful calls; preserve quota failures. Groq baseline calls require a valid key and network. Never print keys.

## 8. HaluEval commands

```powershell
python -m evaluation.benchmark_runner --dataset data/halu_eval/general_data.json --samples 10 --seed 42
python -m evaluation.benchmark_runner --dataset data/halu_eval/general_data.json --samples 50 --seed 42
python -m evaluation.benchmark_runner --dataset data/halu_eval/general_data.json --samples 100 --seed 42
```

Outputs are written below `results/halueval_<n>/`. The 100-sample run is slow; stop safely with `Ctrl+C`, and count records labelled `error` as failed rather than successful.

## 9. GTR and comparison

```powershell
python scripts/verify_gtr_local.py
python scripts/validate_gtr_index.py
python scripts/test_gtr.py --offline
python -m scripts.gtr_offline_smoke
python -m evaluation.paper_comparison --run-gtr --dataset data/halu_eval/general_data.json --samples 10 --seed 42 --offline
python -m evaluation.comparative_runner --dataset data/halu_eval/general_data.json --samples 10 --seed 42
```

Confirm GTR output names the GTR model, `paper/GTR` mode, and 768 dimensions. Ten samples are too small to claim model superiority; compare accuracy, precision, recall, F1, confusion counts, and latency only descriptively.

## 10. Performance

```powershell
python -m evaluation.profile_pipeline --dataset data/halu_eval/general_data.json --sample-index 0
python -m evaluation.performance_validation --dataset data/halu_eval/general_data.json --sample-index 0
python -m evaluation.generate_performance --predictions results/halueval_100/predictions.json
```

Cold means first model/index load; warm means process caches are retained. Cache hits/misses and retrieval/NLI/total timings are measurements, not estimates.

## 11. Tests and security

```powershell
python -m compileall -q app.py services extraction verification evaluation retrieval analysis visualization scripts
python -m pytest -q
python -m pytest -q tests
git check-ignore -v .env
rg -n -i --glob '!.env' --glob '!*.log' --glob '!.venv/**' 'AIza[0-9A-Za-z_-]{20,}|gsk_[0-9A-Za-z_-]{20,}|sk-[0-9A-Za-z_-]{20,}' .
```

The current validated result is 62 passed, 1 skipped for the full suite and 62 passed for `tests` (three deprecation warnings). If pytest reports Windows temp permission errors, use a normal-permission PowerShell session; do not change production code.

## 12. Troubleshooting

| Problem | Cause / check | Safe fix |
|---|---|---|
| Python/pip not found | `python --version`, `python -m pip --version` | Install Python, reopen PowerShell |
| Activation blocked | Execution policy | Use `Set-ExecutionPolicy -Scope Process Bypass`, then activate |
| Missing package | Import error | `python -m pip install -r requirements.txt` |
| Port occupied | Streamlit port error | Use `--server.port 8502` |
| Gemini 429 | Quota exhausted | Stop retries; mark baseline incomplete |
| Groq API error | Key, model, or network | Check masked configuration and connectivity; never print key |
| Hugging Face refused | Offline/network restriction | Use `--offline` with cached models or restore network |
| GTR model/index missing | Required local artifacts absent | Run the documented rebuild command only when necessary |
| DeBERTa not cached | Offline NLI load failure | Install/cache the exact configured model; do not substitute |
| FAISS index missing | Index files absent | Rebuild the corresponding mode only |
| Wikipedia unavailable | Network/API failure | Continue with local evidence; record fallback unavailable |
| pytest permission error | Windows temp cleanup | Use normal permissions and a clean workspace temp location |
| CUDA unavailable | No GPU | CPU execution is supported; expect longer latency |
| Model loads slowly | First load/cache | Wait for cold load; use warm process for repeated checks |

## START HERE (live demo)

```powershell
cd D:\halu
if (Test-Path .venv\Scripts\Activate.ps1) { .\.venv\Scripts\Activate.ps1 }
python -c "from utils.env_utils import load_environment; load_environment(); import os; print('Provider configured:', os.getenv('LLM_PROVIDER','groq')); print('Groq key present:', bool(os.getenv('GROQ_API_KEY'))); print('Gemini key present:', bool(os.getenv('GEMINI_API_KEY')))"
python scripts/test_nli_model.py --offline
python scripts/test_gtr.py --offline
python scripts/validate_gtr_index.py
python -m streamlit run app.py
```

## RESEARCH EXPERIMENT RUN (optional/slow)

```powershell
cd D:\halu
python -m evaluation.benchmark_runner --dataset data/halu_eval/general_data.json --samples 10 --seed 42
python -m evaluation.benchmark_runner --dataset data/halu_eval/general_data.json --samples 50 --seed 42
python -m evaluation.benchmark_runner --dataset data/halu_eval/general_data.json --samples 100 --seed 42
python -m evaluation.paper_comparison --run-gtr --dataset data/halu_eval/general_data.json --samples 10 --seed 42 --offline
python -m evaluation.profile_pipeline --dataset data/halu_eval/general_data.json --sample-index 0
python -m evaluation.performance_validation --dataset data/halu_eval/general_data.json --sample-index 0
python -m pytest -q tests
```

Gemini commands are `[REQUIRES API]`; Wikipedia and provider calls are `[REQUIRES INTERNET]`; model/index checks with cached artifacts are `[OFFLINE]`; benchmarks and GTR are `[OPTIONAL / SLOW]`.

## React + FastAPI local execution

Install backend dependencies into the project virtual environment (important
when system Python differs from `.venv`):

```powershell
cd D:\halu
.\.venv\Scripts\Activate.ps1
python -m pip install fastapi "uvicorn[standard]"
python -c "import fastapi,uvicorn; print(fastapi.__version__, uvicorn.__version__)"
```

Start the complete application with `D:\halu\start_halucheck.bat`, or use two
terminals:

```powershell
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
cd frontend
npm run dev
```

Open `http://localhost:5173`. Verify the backend directly at
`http://127.0.0.1:8000/api/health`, `/api/history`, `/api/settings`, and
`/api/config`; Swagger is at `/docs`.
