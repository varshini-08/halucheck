# HaluCheck 5–10 Minute Demo Script

1. Introduce HaluCheck as an explainable hallucination detector.
2. Explain the problem: fluent LLM answers can contain unsupported claims.
3. Show the React dashboard and provider status.
4. Enter `Why does Earth revolve around the Sun?` and click Analyze.
5. Explain the concise answer and extracted atomic claims.
6. Show source routing and expand one Evidence accordion.
7. Explain DeBERTa-v3 MNLI labels: Supported, Contradicted, and Neutral.
8. Point out support rate, neutral rate, hallucination rate, evidence coverage, and processing time.
9. Run a false claim such as `Paris is the capital of Germany` and discuss the measured result.
10. Open Dashboard and History to show persisted analyses.
11. Export the current analysis and show that it contains claims, evidence, metrics, and timing without secrets.
12. Explain multi-source adapters, caching, batching, and known limitations.
13. Conclude that HaluCheck provides traceable evidence rather than an unexplained score.

Use `DEMO_TEST_CASES.md` for the official question list. Record only observed outputs.
