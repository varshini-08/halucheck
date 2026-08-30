# End-to-End Validation Status

The production chain is wired as:

`question → Groq response → spaCy processing → atomic facts → entities → local FAISS → Wikipedia fallback → evidence ranking → DeBERTa NLI → fact labels → response classification → Streamlit rendering`.

Automated evidence: component and integration tests pass (`60 passed, 1 skipped`), controlled extraction validation passes, and the benchmark runner invokes the existing `HaluCheckPipeline.analyse` path.

Live end-to-end Groq/Wikipedia/NLI cases and browser rendering were not executed in this pass because they require external API/model resources or an interactive browser. They are listed in `docs/manual_ui_validation.md`; no live results are fabricated.
