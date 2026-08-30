# Performance Benchmark

The latest measured live Groq Earth analysis completed in approximately 18–19 seconds with four claims. API timing metadata exposes LLM, extraction, retrieval, NLI, total, and persistence timings. NLI resources are process-cached and inference is batched.

Historical runs varied from approximately 18 to 361 seconds depending on model warm-up, local retrieval state, and external/network conditions. A controlled multi-run benchmark with configured external adapters is still required before claiming a universal latency target.
