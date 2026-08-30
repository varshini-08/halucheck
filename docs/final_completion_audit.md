# Final Completion Audit

## Architecture

Question → Groq response → spaCy sentence processing → atomic facts → entities/matching → local FAISS → Wikipedia fallback → evidence ranking → DeBERTa NLI → fact labels → response hallucination classification → Streamlit.

## Technologies/models

Groq `openai/gpt-oss-20b`, spaCy `en_core_web_sm`, RapidFuzz, SentenceTransformers `all-MiniLM-L6-v2`, FAISS, Wikipedia API, DeBERTa-v3-MNLI, Streamlit, and official HaluEval data.

## Existing evidence

- Full suite: 62 passed, 1 skipped, 3 warnings.
- HaluEval data: 4,507 records; 815 hallucination and 3,692 non-hallucination.
- Validated benchmark directories: `results/halueval_10/`, `results/halueval_50/`.
- Current/GTR mode separation is tested; GTR artifacts are not available.

## Missing or blocked

- 100-sample benchmark: runtime constrained.
- GTR experiment: model/index unavailable.
- SelfCheckNLI: one response per prompt.
- LLM baseline: API key not configured.
- Browser screenshots: manual interactive session required.
- Exact paper decomposition/aggregation: public methodology incomplete.

No production algorithm or existing result was removed.
