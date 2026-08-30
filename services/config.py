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
MAX_CLAIMS = max(1, int(os.getenv("MAX_CLAIMS", "8")))
NLI_BATCH_SIZE = max(1, int(os.getenv("NLI_BATCH_SIZE", "8")))
NLI_MAX_LENGTH = max(64, int(os.getenv("NLI_MAX_LENGTH", "512")))
NLI_DEVICE = os.getenv("NLI_DEVICE", "auto").strip().lower()
MAX_EVIDENCE_PER_CLAIM = max(1, int(os.getenv("MAX_EVIDENCE_PER_CLAIM", "3")))
MAX_TOTAL_EVIDENCE = max(1, int(os.getenv("MAX_TOTAL_EVIDENCE", "20")))
SOURCE_CACHE_TTL = max(1, int(os.getenv("SOURCE_CACHE_TTL", "3600")))
MAX_LLM_RESPONSE_TOKENS = max(64, int(os.getenv("MAX_LLM_RESPONSE_TOKENS", "256")))
EVIDENCE_RELEVANCE_THRESHOLD = float(os.getenv("EVIDENCE_RELEVANCE_THRESHOLD", "0.55"))
VERIFICATION_MODE = os.getenv("VERIFICATION_MODE", "BALANCED").strip().upper()
