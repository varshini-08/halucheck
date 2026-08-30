"""Environment-backed configuration for hybrid evidence retrieval."""
from __future__ import annotations
import os

ENABLE_WIKIPEDIA_FALLBACK = os.getenv("ENABLE_WIKIPEDIA_FALLBACK", "true").strip().lower() in {"1", "true", "yes", "on"}
LOCAL_SIMILARITY_THRESHOLD = float(os.getenv("LOCAL_SIMILARITY_THRESHOLD", "0.60"))
MAX_WIKIPEDIA_CHUNKS = int(os.getenv("MAX_WIKIPEDIA_CHUNKS", "3"))
WIKIPEDIA_REQUEST_TIMEOUT = float(os.getenv("WIKIPEDIA_REQUEST_TIMEOUT", "10"))
WIKIPEDIA_USER_AGENT = os.getenv("WIKIPEDIA_USER_AGENT", "HaluCheck/1.0 (Educational Project)")
RETRIEVAL_MODE = os.getenv("RETRIEVAL_MODE", "current").strip().lower()
CURRENT_RETRIEVAL_MODEL = "all-MiniLM-L6-v2"
PAPER_RETRIEVAL_MODEL = "sentence-transformers/gtr-t5-base"
