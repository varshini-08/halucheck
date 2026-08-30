# Technology Stack

| Technology | Purpose | Where used |
|---|---|---|
| Python | Application and evaluation code | Entire project |
| Groq / `openai/gpt-oss-20b` | Response generation | `services/llm_service.py`, `app.py` |
| spaCy | Sentence parsing and entities | `extraction/` |
| RapidFuzz | Fuzzy entity matching | `verification/entity_matcher.py` |
| SentenceTransformers / `all-MiniLM-L6-v2` | Embeddings | `services/retriever.py`, index builder |
| FAISS | Vector search | `services/vector_store.py` |
| Wikipedia API | Fallback evidence | `services/wikipedia_service.py` |
| DeBERTa-v3-MNLI | Entailment verification | `verification/nli_verifier.py` |
| Streamlit | Interactive dashboard | `app.py`, `visualization/` |
| HaluEval | Benchmark dataset | `data/halu_eval/`, `evaluation/` |
