# Final Repository Audit

| Component | File(s) | Purpose | Status | Coverage | Limitation |
|---|---|---|---|---|---|
| Generation | `services/llm_service.py`, `app.py` | Groq response generation | PASS | service/app tests | Requires `GROQ_API_KEY` for live calls |
| Extraction | `extraction/atomic_fact_extractor.py` | Atomic facts and entities | PASS | extractor/entity tests | spaCy model required |
| Retrieval | `services/retriever.py`, `services/vector_store.py` | Local FAISS and caching | PASS | retriever/vector tests | Model/index resources required |
| Wikipedia | `services/wikipedia_service.py` | Fallback evidence | PASS | Wikipedia tests | Network dependent |
| Verification | `verification/` | DeBERTa NLI and classification | PASS | NLI tests | Model inference resource dependent |
| Evaluation | `evaluation/` | HaluEval, comparisons, reports | PASS | evaluation tests | Large runs are slow |
| UI | `app.py`, `visualization/dashboard.py` | Streamlit dashboard | PASS | import tests | Browser validation not automated |
| Paper mode | `evaluation/paper_*`, `scripts/build_index.py` | Optional GTR/approximate modes | PARTIAL | paper-mode tests | GTR index unavailable; paper details incomplete |

Production flow: input → Groq response → spaCy sentences → atomic facts → entities → local FAISS → Wikipedia fallback → evidence ranking → DeBERTa NLI → fact classification → response hallucination classification → dashboard.
