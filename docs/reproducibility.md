# Reproducibility Instructions

## Setup

Use Python 3.13 in the validated environment:

`pip install -r requirements.txt`

Create `.env` from `.env.example` and set `GROQ_API_KEY` only for live Groq generation. Install spaCy data and build the production index:

`python -m spacy download en_core_web_sm`

`python scripts/build_index.py --retrieval-mode current`

## Validation

`python -m evaluation.technology_validation`

`python -m evaluation.final_validation`

`python -m pytest -q`

## Benchmarks

`python -m evaluation.benchmark_runner --dataset data/halu_eval/general_data.json --samples 10 --seed 42`

`python -m evaluation.benchmark_runner --dataset data/halu_eval/general_data.json --samples 50 --seed 42`

## Optional GTR

`python scripts/test_gtr.py`

`python scripts/build_index.py --retrieval-mode paper`

`python -m evaluation.paper_comparison --run-gtr --dataset data/halu_eval/general_data.json --samples 10 --seed 42`

GTR uses a separate index and never replaces the production MiniLM index. It requires a large model download.

## Limitations

The 100-sample run is runtime-intensive. SelfCheckNLI requires multiple independent responses, which the official general dataset does not provide. The LLM baseline requires an API key. Browser validation requires manual interactive execution. Exact paper decomposition and aggregation are not fully specified publicly.
