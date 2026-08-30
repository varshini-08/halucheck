# Reproducibility Guide

Use Python 3.13 (the validated environment) and install dependencies with `pip install -r requirements.txt`.

Set `GROQ_API_KEY` only for live generation or the opt-in LLM baseline. The official HaluEval file is `data/halu_eval/general_data.json`.

Build the production index with `python scripts/build_index.py --retrieval-mode current`, then start the UI with `streamlit run app.py`.

Run the validated-size benchmark:

`python -m evaluation.benchmark_runner --dataset data/halu_eval/general_data.json --samples 50 --seed 42`

Run comparative evaluation:

`python -m evaluation.comparative_runner --dataset data/halu_eval/general_data.json --samples 10 --seed 42`

Run deterministic validation artifacts:

`python -m evaluation.final_validation`

Generate performance output from predictions:

`python -m evaluation.generate_performance --predictions results/halueval_50/predictions.json`

GTR is optional and isolated: `python scripts/build_index.py --retrieval-mode paper`. It writes `vector_db/gtr_base.index` and never replaces the MiniLM index. SelfCheckNLI needs multiple independent responses and cannot be validly evaluated from the single-response general dataset. The LLM baseline requires an API key and is never run automatically.

Run tests with `python -m pytest -q`.
