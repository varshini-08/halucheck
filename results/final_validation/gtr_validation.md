# GTR Validation

## Model and smoke test

The explicit smoke test is `python scripts/test_gtr.py`. It loads only `sentence-transformers/gtr-t5-base`, requires a 768-dimensional result, and never falls back to MiniLM.

## Index

`python scripts/build_index.py --retrieval-mode paper` writes the separate `vector_db/gtr_base.index`, `vector_db/gtr_base_metadata.pkl`, and `vector_db/gtr_base_manifest.json`. The manifest records model, dimension, vector count, metadata count, index type, mode, and timestamp. The production `vector_db/vector.index` is not touched.

## Current status

GTR model download/index creation was not completed in this environment. `python -m evaluation.paper_comparison` therefore reports the paper mode as unavailable. No GTR retrieval or HaluEval metrics are claimed.
