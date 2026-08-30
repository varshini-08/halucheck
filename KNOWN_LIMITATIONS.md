# Known Limitations

- Optional external source adapters are not all configured or implemented in the default environment.
- Browser click-through, responsive visual checks, and Gemini quota validation require manual testing.
- Windows pytest can report access-denied cleanup errors when stale temporary directories are held by another process.
- Performance varies with CPU/GPU, model warm-up, local index state, and network providers.
