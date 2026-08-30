# Final Evidence Index

Screenshots listed below are required manual evidence; none are fabricated by this repository.

| Area | Screenshot | What it proves | Related code/report |
|---|---|---|---|
| System overview | `01_dashboard.png` | Application shell and dashboard | `frontend/src/App.tsx`, `FINAL_RELEASE_REPORT.md` |
| Analysis input | `02_new_analysis.png` | Question entry and provider | `frontend/src/App.tsx` |
| AI response | `03_ai_response.png` | Concise generated answer | `services/llm_service.py` |
| Verification | `04_fully_verified.png` | Fully supported result | `api/main.py` |
| Partial result | `05_partially_verified.png` | Neutral/unverified distinction | `frontend/src/main.tsx` |
| Contradiction/neutral | `06_contradicted_or_neutral.png` | Error/uncertainty handling | `verification/fact_classifier.py` |
| Evidence | `07_evidence_expanded.png` | Source, text, scores | `frontend/src/App.tsx` |
| History | `08_history.png` | Persistent analyses | `api/storage.py` |
| Export | `09_export_report.png` | Current analysis export | `frontend/src/App.tsx` |
| Provider | `10_settings_provider.png` | Dynamic provider state | `/api/provider/status` |
| About | `11_about.png` | Project information | `frontend/src/App.tsx` |
| Responsive | `12_responsive_mobile.png` | Mobile layout | `frontend/src/styles.css` |
| API | `13_swagger_api.png` | FastAPI endpoints | `api/main.py` |
| Repository | `14_github_repository.png` | GitHub release | Git history |
| Tests | `15_test_results.png` | Automated validation | `TESTING.md` |

Capture these manually after starting the app. Hide credentials and personal information.
