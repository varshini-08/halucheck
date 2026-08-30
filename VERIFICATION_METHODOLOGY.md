# Verification Methodology

Answers are split into atomic factual propositions. Meta, instructional, question, incomplete, and duplicate propositions are filtered. Evidence is normalized, deduplicated, relevance-filtered, and ranked before batched DeBERTa-v3 MNLI inference. `SUPPORTED` requires strong entailment, `CONTRADICTED` requires strong contradiction, and `NEUTRAL` means available evidence is insufficient.

Metrics are independent: hallucination rate = contradicted/total; support rate = supported/total; neutral rate = neutral/total; evidence coverage = claims with evidence/total.
