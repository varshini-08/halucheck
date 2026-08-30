# Demonstration Test Cases

1. **Factual:** “Paris is the capital of France.” Expect supported evidence.
2. **Hallucinated:** “Paris is the capital of Australia.” Expect contradiction when evidence is available.
3. **Mixed:** Combine one supported and one false claim; point out mixed fact labels and response-level policy.
4. **Entity-heavy:** “Apple was founded by Steve Jobs.” Show PERSON/ORG entities.
5. **Date/number:** “Ada Lovelace wrote notes in 1843.” Show preserved date.
6. **Local KB:** Ask about a document in `knowledge_base/wikipedia.json`.
7. **Wikipedia fallback:** Use a query absent from the local corpus with fallback enabled.
8. **Unknown:** Use unsupported information; expect neutral/insufficient evidence.
9. **Empty input:** Submit no question; expect validation feedback.
10. **Long response:** Paste a multi-sentence response; show extraction and evidence sections.

These are demonstration scripts, not precomputed results.
