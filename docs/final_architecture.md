# HaluCheck Architecture

```text
User question → Groq LLM → generated response → sentence processing
→ atomic facts → entity detection/matching → evidence retrieval
→ local FAISS knowledge base (first) / Wikipedia fallback
→ evidence ranking → DeBERTa-v3-MNLI
→ SUPPORTED / CONTRADICTED / NEUTRAL
→ response hallucination classification → Streamlit dashboard
```

The local index is attempted first. Wikipedia is used only when local evidence is insufficient and fallback is enabled. Phase 4 evaluation calls the same analysis pipeline from a CLI runner.
