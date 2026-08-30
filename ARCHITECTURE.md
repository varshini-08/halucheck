# HaluCheck Architecture

React/Vite provides the browser UI and calls the FastAPI adapter. FastAPI invokes the selected LLM provider, then `HaluCheckPipeline` extracts atomic facts, retrieves local/optional external evidence, and verifies evidence with cached, batched DeBERTa-v3 MNLI. Results are serialized, stored in SQLite, and used by dashboard/history/export views.

The provider credentials remain backend-only. Source adapters are routed by claim/domain and unavailable adapters are isolated from the request.
