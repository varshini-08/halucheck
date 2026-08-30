# Viva Questions and Answers

1. **What is hallucination?** A generated claim that is unsupported or contradicted by evidence.
2. **Why detect it?** Incorrect claims reduce trust and can cause harm.
3. **Why atomic facts?** Smaller claims can be retrieved and verified independently.
4. **Why spaCy?** It provides deterministic sentence and dependency parsing.
5. **Why FAISS?** It makes semantic nearest-neighbor retrieval efficient.
6. **Why SentenceTransformers?** It maps text to comparable semantic vectors.
7. **Why MiniLM?** It is a practical production embedding model with low latency.
8. **Why Wikipedia?** It supplies an external fallback source when local evidence is weak.
9. **Why local retrieval first?** It is faster, reproducible, and avoids unnecessary network calls.
10. **What is caching?** Reusing embeddings, retrievals, or articles for repeated inputs.
11. **Why can Wikipedia be slow?** Network search and article requests add latency.
12. **What is NLI?** Natural Language Inference compares a premise with a hypothesis.
13. **What is entailment?** The premise supports the hypothesis.
14. **What is contradiction?** The premise conflicts with the hypothesis.
15. **What is neutral?** The evidence is insufficient to decide.
16. **Why three labels?** Support, contradiction, and uncertainty are distinct outcomes.
17. **Why DeBERTa?** It provides pretrained MNLI inference for evidence checking.
18. **What is Groq used for?** Generating the response to be analyzed.
19. **What if Groq fails?** The application reports a user-friendly error.
20. **What if Wikipedia fails?** Local evidence remains available and the failure is handled.
21. **What if no evidence exists?** The fact remains neutral/uncertain under the current policy.
22. **How is a response classified?** A contradicted fact makes the response hallucinated.
23. **What is HaluEval?** A human-annotated hallucination benchmark.
24. **Why use it?** It provides reproducible labeled evaluation data.
25. **What is accuracy?** Correct predictions divided by all evaluated predictions.
26. **What is precision?** Correct hallucination predictions divided by predicted hallucinations.
27. **What is recall?** Detected hallucinations divided by actual hallucinations.
28. **What is F1?** The harmonic mean of precision and recall.
29. **What is TP?** A hallucination correctly predicted as hallucination.
30. **What is TN?** A non-hallucination correctly predicted as non-hallucination.
31. **What is FP?** A non-hallucination incorrectly flagged.
32. **What is FN?** A hallucination missed by the system.
33. **Why confidence?** It communicates the model’s strongest evidence score.
34. **What is the paper methodology?** Retrieval-supported atomic claim verification with NLI.
35. **What matches?** HaluEval, NLI-based verification, and evidence-oriented classification.
36. **What differs?** Production uses MiniLM by default; exact paper decomposition is underspecified.
37. **Why not paper-exact?** Some algorithms and aggregation details are not fully published.
38. **Why is GTR optional?** It is isolated for comparison and must not replace production MiniLM.
39. **Why no SelfCheckNLI result?** The dataset has one response per prompt, not multiple samples.
40. **Why not run 10,000 samples?** Runtime and resource cost are not justified during development.
41. **What is the dashboard role?** It provides an interactive explanation of individual analyses.
42. **What is the CLI role?** It runs repeatable benchmark experiments without clicking the UI.
43. **How are results reproducible?** Fixed random seeds and original benchmark responses are used.
44. **How are secrets protected?** API keys come from environment variables and are not reported.
45. **What is the main bottleneck?** Model initialization/inference and external retrieval can dominate latency.
46. **How is retrieval validated?** Index persistence, ranking, malformed inputs, fallback, and caching are tested.
47. **How is extraction validated?** Regression cases cover subjects, objects, dates, numbers, and modifiers.
48. **What is a limitation?** External APIs, model downloads, and incomplete paper details affect reproduction.
49. **What future work is planned?** GTR, valid SelfCheckNLI data, LLM baseline, and larger runs.
50. **What is the conclusion?** HaluCheck is a tested, explainable, paper-inspired verification system.
