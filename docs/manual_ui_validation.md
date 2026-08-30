# Manual UI Validation Checklist

Validation date: 2026-08-30. Streamlit startup was validated headlessly (HTTP 200). Every interaction below remains MANUAL unless explicitly marked otherwise; no screenshots are fabricated.

| ID | Test case | Expected result | Status | Screenshot |
|---|---|---|---|---|
| UI-01 | Home page | HaluCheck workspace loads | PASS: headless HTTP 200 | Not captured |
| UI-02 | Groq provider | Groq can be selected and key status shown | MANUAL | Required |
| UI-03 | Gemini provider | Gemini can be selected and key status shown | MANUAL | Required |
| UI-04 | Gemini connected state | Configured Gemini displays connected status | MANUAL / API | Required |
| UI-05 | Question submission | Verify button accepts non-empty question | MANUAL | Required |
| UI-06 | Response generation | Generated response renders | MANUAL / API | Required |
| UI-07 | Atomic fact extraction | Individual facts are displayed | MANUAL | Required |
| UI-08 | Entity detection | Detected entities appear in fact details | MANUAL | Optional |
| UI-09 | Local FAISS retrieval | Local evidence cards render | MANUAL | Required |
| UI-10 | Wikipedia fallback | Fallback evidence appears when local evidence is insufficient | MANUAL / Internet | Required |
| UI-11 | Evidence display | Evidence text and source links render | MANUAL | Required |
| UI-12 | DeBERTa verification | Supported/contradicted/neutral labels render | MANUAL | Required |
| UI-13 | Hallucination classification | Percentage and severity are shown | MANUAL | Required |
| UI-14 | Dashboard | Summary, timings, counts, and facts are readable | MANUAL | Required |
| UI-15 | Developer Details collapsed | Details are collapsed by default | MANUAL | Required |
| UI-16 | Developer Details expanded | Details expand and collapse correctly | MANUAL | Required |
| UI-17 | Empty input | Action is disabled or a safe validation error appears | MANUAL | Required |
| UI-18 | Invalid/unusual input | User-facing error is clean and non-secret | MANUAL | Optional |
| UI-19 | Long response | Layout remains usable and scrollable | MANUAL | Optional |
| UI-20 | Regenerate/new analysis | Regenerate runs a new analysis and history remains usable | MANUAL / API | Required |

Suggested inputs include “Who created Python?”, an obviously false date claim, a mixed factual/hallucinated response, an entity/date question, a local-KB topic, an absent topic for Wikipedia fallback, and an imaginary entity for no-evidence behavior. Capture screenshots only in a real browser with API keys obscured.
