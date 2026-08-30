# Evaluation Guide

Run the stable benchmark:

`python -m evaluation.benchmark_runner --dataset data/halu_eval/general_data.json --samples 100 --seed 42`

Run configuration comparison:

`python -m evaluation.comparative_runner --dataset data/halu_eval/general_data.json --samples 10 --seed 42`

Check GTR prerequisites:

`python -m evaluation.paper_comparison`

SelfCheck mode reports unavailable unless multiple responses are supplied; LLM
judge mode is opt-in and requires `GROQ_API_KEY`.
