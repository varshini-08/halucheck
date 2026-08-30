# DeBERTa Offline Validation — 2026-08-30

- Model: `MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli`
- Cache snapshot: `6f5cf0a2b59cabb106aca4c287eed12e357e90eb`
- Required files present: `config.json`, `model.safetensors` (368,877,646 bytes), `spm.model`, `tokenizer.json`, `tokenizer_config.json`, special-token files.
- Offline command: `python scripts/test_nli_model.py --offline`
- Result: PASS — tokenizer and model loaded from the local snapshot without a hub request; supported example returned `SUPPORTED` at 96.78% confidence.
- Additional local checks: a direct entailment pair returned `SUPPORTED` (0.9980); a direct contradiction pair returned `CONTRADICTED` (0.9971). Probability totals were approximately 1.0, allowing float16 rounding.

The previous failure was caused by the smoke script using non-offline mode, not by a missing cached checkpoint. No fallback NLI model was used.
