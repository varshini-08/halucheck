# System Flow

| Stage | Input | Process | Output |
|---|---|---|---|
| Generation | Question | Groq completion | LLM response |
| Sentence processing | Response | spaCy segmentation | Sentences |
| Atomic extraction | Sentences | Deterministic dependency-aware splitting | Atomic facts |
| Entity detection | Facts | spaCy supported labels | Entities |
| Matching | Entities | Exact/substring/fuzzy label-aware comparison | Consistency report |
| Retrieval | Facts | FAISS first, Wikipedia fallback | Evidence passages |
| NLI | Evidence + fact | DeBERTa premise/hypothesis inference | Probabilities/label |
| Classification | Fact labels | Existing policy aggregation | Hallucination verdict |
| Dashboard | Analysis result | Render evidence and summaries | Explainable UI |
