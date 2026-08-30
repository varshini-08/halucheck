# Manual UI Validation

Validation date: 2026-08-30.

The application was started with `python -m streamlit run app.py --server.headless true --server.port 8503`. It returned HTTP 200 with non-empty content. This validates startup only; no browser clicks or screenshots are claimed.

| Test ID | Test description | Expected result | Actual result | Status | Screenshot |
|---|---|---|---|---|---|
| UI-01 | Application startup | Streamlit serves the application | HTTP 200, non-empty response | PASS | Not captured (headless) |
| UI-02 | Groq provider selection | Provider can be selected and key status shown | Static UI implementation inspected; not interacted with | MANUAL REQUIRED | — |
| UI-03 | Gemini provider selection | Provider can be selected and key status shown | Static UI implementation inspected; not interacted with | MANUAL REQUIRED | — |
| UI-04 | Question input / empty input | Input accepts text and disabled action prevents empty submission | Not interacted with | MANUAL REQUIRED | — |
| UI-05 | Generation and error handling | Response renders or a safe user-facing error is shown | Requires a valid provider key and live call | NOT RUN | — |
| UI-06 | Fact labels and evidence | Supported, contradicted, neutral, and evidence displays render | Requires successful analysis | NOT RUN | — |
| UI-07 | Summary | Hallucination percentage, severity, evidence count, and time display | Requires successful analysis | NOT RUN | — |
| UI-08 | History / regenerate | Conversation history and regenerate action work | Requires successful analysis | NOT RUN | — |
| UI-09 | Developer Details | Collapsed by default and expandable | Not interacted with | MANUAL REQUIRED | — |
| UI-10 | Long response | Layout remains usable | Requires controlled live response | NOT RUN | — |

Screenshots must be captured during a local browser session with API keys obscured. Do not treat this headless startup check as a replacement for manual UI validation.
