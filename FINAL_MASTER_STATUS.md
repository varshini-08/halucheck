# HaluCheck Final Master Status

Validation date: 2026-08-30. This is the authoritative final status; older phase reports are historical snapshots.

| Item | Status | Evidence / command | Result and limitation |
|---|---|---|---|
| Production system | GREEN | `python -m pytest -q` | 62 passed, 1 skipped |
| Groq | GREEN | Controlled request with local `.env` key | Request succeeded; key remains local and ignored |
| Gemini | YELLOW | detailed baseline artifact | Integration implemented; quota-limited baseline incomplete |
| Atomic extraction | GREEN | automated tests | Covered by passing suite |
| Entity matching | GREEN | automated tests | Covered by passing suite |
| MiniLM retrieval | GREEN | offline load/isolation check | 384d; `vector_db/vector.index` only |
| Wikipedia | YELLOW | implementation/tests | Implemented; no live fallback call in this audit |
| GTR | GREEN | `scripts/test_gtr.py --offline` | 768d, separate index, 10-sample result validated |
| DeBERTa NLI | GREEN | `scripts/test_nli_model.py --offline` | Cached model loads locally; no fallback |
| Hallucination classification | GREEN | automated tests | Covered by passing suite |
| HaluEval 10 / 50 / 100 | GREEN | preserved metrics artifacts | 10/10, 50/50, 99/100 valid respectively |
| Comparative evaluation | GREEN | comparison artifacts | Existing results preserved; small comparison not superiority proof |
| Gemini baseline | RED | `results/baselines/llm_gemini` | 1 valid / 10 attempts; quota limitation |
| SelfCheckNLI | RED | dataset inspection | Single response per prompt; multi-response data required |
| Browser validation | YELLOW | Streamlit HTTP 200 | Startup pass; manual browser evidence pending |
| Security | GREEN | pattern scan and `.gitignore` | No literal provider secret pattern outside excluded secret/log files |
| Performance | YELLOW | preserved performance artifacts | Existing measurements retained; no new complete live-profile run claimed |
| Automated tests | GREEN | pytest | 62 passed, 1 skipped; 3 warnings |
| Paper alignment | YELLOW | `docs/final_paper_alignment.md` | Partial / paper-inspired, not exact |
| Cost analysis | RED | project inspection | Not verified; no authoritative price plus measured tokens |
| Documentation | GREEN | final audit documents | Final evidence reports updated |
| Reproducibility | YELLOW | commands below | Requires cached models and valid provider credentials for live calls |

## Remaining actions

1. Perform the checklist in `docs/manual_ui_validation.md` in a real browser and capture redacted screenshots.
2. Re-run Gemini only after quota is available and retain all outcomes.
3. Obtain a legitimate multi-response dataset before attempting SelfCheckNLI.
4. Obtain provider token accounting and official pricing before a cost claim.

## Reproduction commands

```powershell
python -m compileall -q app.py services extraction verification evaluation retrieval analysis visualization scripts
python -m pytest -q
python -m pytest -q tests
python scripts/test_nli_model.py --offline
python scripts/test_gtr.py --offline
python -m scripts.gtr_offline_smoke
python -m streamlit run app.py --server.headless true
```
