# Algorithm

Claims are split into complete propositions and filtered for metadata, instructions, questions, fragments, and duplicates. Evidence is ranked using semantic relevance and source policy; low-relevance Wikipedia passages are discarded. DeBERTa-v3 MNLI runs batched entailment/contradiction/neutral inference. Supported and contradicted decisions require confidence thresholds; otherwise the result is Neutral.
