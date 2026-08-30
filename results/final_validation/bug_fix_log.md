# Bug Fix Log — 2026-08-30

## NLI offline smoke mode

- Original problem: `scripts/test_nli_model.py` could only run with `offline=False`, so a supposedly local validation could attempt a network request.
- Reproduction: `python scripts/test_nli_model.py` in the restricted network environment.
- Root cause: no command-line offline flag was passed into `NLIVerifier`.
- Change made: added `--offline`; it now calls `NLIVerifier(offline=True)` when selected.
- Validation: `python scripts/test_nli_model.py --offline`.
- Result: PASS. The cached MoritzLaurer DeBERTa model, tokenizer, and `model.safetensors` loaded locally; supported result confidence was 96.78%.

## No production-algorithm changes

No retrieval, NLI-label mapping, extraction, classification, index, or provider-selection algorithm was changed during this audit.
