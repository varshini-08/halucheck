# Test Report

Focused extractor tests pass. The full suite has been executed, but this Windows environment currently raises `PermissionError` while pytest creates temporary directories under the user profile. Those are environment failures, not assertion failures. Re-run with a writable `--basetemp` directory when available.
