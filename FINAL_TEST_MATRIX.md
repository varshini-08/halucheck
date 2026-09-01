# Final Test Matrix

| ID | Category | Question/Scenario | Provider | Actual status |
|---|---|---|---|---|
| TC01 | General fact | Capital of France | Groq | Live Groq path previously passed |
| TC02 | Science | Earth revolves around Sun | Groq | Live path passed; four claims observed |
| TC03 | History | First person on Moon | Groq | Manual evidence required |
| TC04 | Mathematics | 12 × 8 | Groq | Manual evidence required |
| TC05 | False claim | Paris is capital of Germany | Groq | Manual evidence required |
| TC06 | Multi-claim | Independent factual claims | Groq | Manual evidence required |
| TC07 | Ambiguous | Apple | Groq | Manual evidence required |
| TC08 | Medical | What is insulin? | Groq | Manual evidence required |
| TC09 | Statistics | Population/economic fact | Groq | Manual evidence required |
| TC10 | Provider | Groq generation | Groq | PASS; live validated |
| TC11 | Provider | Gemini generation | Gemini | NOT TESTED; quota/configuration dependent |
| TC12 | No evidence | Unsupported niche statement | Groq | Manual evidence required |
| TC13 | UI | Evidence accordion | — | Manual browser required |
| TC14 | Persistence | History after refresh/restart | — | Manual browser required |
| TC15 | Export | Export current analysis | — | Manual browser required |
| TC16 | Switching | Groq ↔ Gemini | — | Manual browser required |
| TC17 | Failure | Optional source timeout | — | Mock/unit coverage; live optional source not configured |
| TC18 | Responsive | Desktop/tablet/mobile layouts | — | Manual browser required |
