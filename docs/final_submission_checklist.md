# Final Submission Checklist

- Source code and `requirements.txt` included.
- Copy `.env.example` to `.env`; set `GROQ_API_KEY` only for live generation or the optional LLM baseline.
- Install the required spaCy model and build the production MiniLM index.
- Dataset: `data/halu_eval/general_data.json`.
- Production index: `vector_db/vector.index` and metadata; optional isolated GTR artifacts are under `vector_db/gtr_base*`.
- Run benchmarks with fixed seed 42; outputs are written under `results/`.
- Run `python -m pytest -q` and compile the application packages.
- Run `streamlit run app.py` for manual UI validation.
- Historical 10/50 results and the 100-attempt result are preserved.
- Known limitations: GTR runtime access, LLM key, SelfCheckNLI data, manual browser evidence, verified pricing, and paper underspecification.

No screenshots are claimed unless manually captured under `results/screenshots/`.
