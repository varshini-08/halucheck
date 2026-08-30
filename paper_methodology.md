# Evaluation Methodology

Production defaults remain unchanged: `all-MiniLM-L6-v2`, local FAISS with Wikipedia fallback, and DeBERTa-v3-MNLI. Paper experiments are opt-in and isolated.

The official HaluEval general dataset contains one response per sample. Therefore
SelfCheckNLI cannot be reproduced without generating additional stochastic
responses; this project does not generate them automatically.
