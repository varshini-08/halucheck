# HaluCheck Viva Questions and Answers

## Project basics

1. **What is HaluCheck?** An explainable system that checks generated claims against retrieved evidence.
2. **What problem does it solve?** It identifies unsupported or contradicted statements in fluent LLM responses.
3. **Why is hallucination detection needed?** Fluency does not guarantee factual correctness.
4. **What are the objectives?** Generate, decompose, retrieve evidence, verify, explain, and persist results.
5. **What is the main output?** Claim-level Supported, Contradicted, or Neutral results with evidence.

## Architecture

6. **Explain the architecture.** React calls FastAPI; FastAPI invokes the provider and HaluCheck pipeline; results return to React and SQLite.
7. **Why FastAPI?** It provides typed, testable HTTP endpoints and safe backend credential handling.
8. **Why React/Vite?** It provides a responsive interactive dashboard without exposing provider keys.
9. **Why FAISS?** It enables efficient similarity search over the local knowledge base.
10. **Why multiple sources?** Different domains require different authoritative evidence.

## LLM

11. **Why Groq?** It provides fast hosted inference through a backend SDK.
12. **Why Gemini?** It provides a second provider option through the same abstraction.
13. **What happens when a provider fails?** The API returns a sanitized typed error; credentials are never returned.
14. **Why constrain the answer prompt?** Concise factual output reduces meta text and unnecessary claims.

## Claims

15. **What is an atomic claim?** A self-contained factual proposition that can be checked independently.
16. **Why split responses?** Verification is more precise at claim level than for a whole paragraph.
17. **Why filter meta claims?** Instructions and user-intent statements are not factual propositions.
18. **How are duplicate claims handled?** Normalized signatures and lexical overlap remove near-duplicates.
19. **What limits claim growth?** Configurable `MAX_CLAIMS`, defaulting to eight in the production pipeline.

## Retrieval

20. **How is evidence retrieved?** Claims are routed to local FAISS, Wikipedia, and configured adapters.
21. **Why semantic retrieval?** Meaning-based similarity is more robust than keyword matching alone.
22. **How is relevance determined?** Evidence is embedded, scored, filtered by threshold, and ranked.
23. **How are duplicates removed?** Normalized evidence and source-aware deduplication remove repeats.
24. **What if a source fails?** Other sources continue; unavailable adapters do not terminate analysis.
25. **Why use complete claims for Wikipedia search?** Entity-only searches can select irrelevant disambiguation pages.

## NLI verification

26. **What is NLI?** Natural-language inference estimates entailment, contradiction, or neutrality between evidence and claim.
27. **Why DeBERTa-v3 MNLI?** It is a pretrained NLI model suitable for evidence/claim comparison.
28. **What is entailment?** The evidence supports the claim.
29. **What is contradiction?** The evidence conflicts with the claim.
30. **What is Neutral?** Available evidence is insufficient to determine support or contradiction.
31. **Why not keyword matching?** Shared words do not prove semantic support.
32. **How is performance improved?** The model/tokenizer are cached and all pairs are processed in batches with inference mode.

## Metrics

33. **How is hallucination rate calculated?** Contradicted claims divided by total claims.
34. **What is support rate?** Supported claims divided by total claims.
35. **What is neutral rate?** Neutral claims divided by total claims.
36. **What is evidence coverage?** Claims with usable evidence divided by total claims.
37. **Is Neutral a hallucination?** No. Neutral means unverified, not disproven.
38. **What does Partially Verified mean?** At least one claim remains neutral/unverified and none of the result semantics are hidden.

## Multi-source and security

39. **Why source adapters?** They isolate provider-specific configuration, parsing, timeout, and failure behavior.
40. **How are source statuses represented?** The registry/API distinguishes available, configured, and not configured sources.
41. **Where are API keys stored?** Backend `.env`, never React or browser payloads.
42. **How is `.env` protected?** It is ignored by Git and not bundled by Vite.

## Limitations and future work

43. **Why are some sources unavailable?** They require credentials, licensing, or additional adapter implementation.
44. **Why can timing vary?** Model warm-up, CPU/GPU hardware, indexes, and network sources affect latency.
45. **What would you improve next?** Controlled benchmarks, more authoritative adapters, and broader evaluation datasets.
46. **How should results be demonstrated?** Show question → answer → claims → evidence → NLI label → metrics.
47. **What is the main research limitation?** Evidence quality bounds verification quality.
48. **What is the release status?** Ready with limitations after automated validation; browser acceptance remains manual.
