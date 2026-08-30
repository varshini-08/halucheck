# Pre-fix Audit — 2026-08-30

| Issue | File | Severity | Reproducibility | Evidence | Recommended fix |
|---|---|---|---|---|---|
| Offline NLI smoke was not selectable | `scripts/test_nli_model.py` | Medium | Confirmed | Script always built `NLIVerifier()` with offline disabled and could invoke the hub metadata path | Add an explicit `--offline` flag and pass it to the verifier |
| Pytest temporary-directory removal fails in sandbox | `pytest.ini` / execution environment | Low | Environment-specific | Restricted sandbox raises WinError 5 on workspace temp cleanup; elevated Windows run passes | Preserve configuration; document normal-permission test command |
| Browser-level validation has no captured evidence | UI validation records | Medium | Confirmed | Only HTTP startup check is available | Keep as manual-required; do not fabricate screenshots |
| Gemini baseline is incomplete | Gemini result artifacts | Medium | Confirmed external limitation | 9/10 detailed records are quota-limited | Preserve artifact; do not retry until quota is available |
| Legacy reports contain stale GTR-blocked snapshots | older Markdown reports | Low | Confirmed | Current GTR artifact is 10/10 successful | Use `FINAL_MASTER_STATUS.md` as authoritative status; retain snapshots as historical evidence |
