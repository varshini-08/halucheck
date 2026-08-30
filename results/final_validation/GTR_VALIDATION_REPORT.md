# GTR Retrieval Validation Report — 2026-08-28

- GTR infrastructure: **COMPLETE**
- Local GTR model validation: **PASS** — `sentence-transformers/gtr-t5-base`, local-only, 768 dimensions, finite `(1, 768)` float16 embedding.
- GTR FAISS index: **PASS** — `vector_db/gtr_base.index`, 768 dimensions, 7 vectors.
- GTR metadata and manifest: **PASS** — 7 metadata records; manifest model, dimension, mode, and counts match the loaded index.
- Offline retrieval smoke test: **PASS** — 3/3 queries returned results from the isolated GTR index, with Wikipedia disabled and no MiniLM fallback.
- GTR 2-sample experiment: **FAIL / BLOCKED** — 2 attempted, 0 successful, 2 failures. The local DeBERTa NLI model is unavailable. Failed calls were excluded from all metrics.
- GTR 10-sample experiment: **NOT RUN** — gated on a successful 2-sample run.
- GTR 50/100-sample experiment: **NOT RUN**.
- GTR vs MiniLM comparison: **NOT RUN** — requires the same successful GTR prediction records.

## Measured GTR retrieval performance

- Model load: 6.932665 s
- Embedding: 0.1597336 s
- FAISS retrieval: 0.0001858 s
- Total cached-query retrieval: 0.0001185 s
- Full verification: null (the local NLI prerequisite is unavailable)

The offline evaluation path now disables Wikipedia fallback, requires the GTR model in paper mode, and propagates `--offline` to DeBERTa so missing local resources fail loudly rather than downloading or being counted as predictions. The production MiniLM index and retrieval mode were not modified.

## Test evidence

- `tests/test_gtr_mode.py`: 2 passed, 1 warning (pytest cache permission warning).
- Full `pytest -q`: 51 passed, 1 skipped, 11 setup errors. The errors are external `PermissionError` failures accessing pytest temporary directories; no test assertion failures were reported. A workspace `--basetemp` retry encountered the same host access denial during pytest cleanup.
- Compilation: PASS — `python -m compileall -q app.py services extraction verification evaluation retrieval analysis visualization scripts`.
