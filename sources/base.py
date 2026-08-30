"""Common contract for optional external evidence adapters."""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
import requests

@dataclass
class Evidence:
    source: str; title: str | None; content: str | None; url: str | None
    source_type: str = "web"; retrieved_at: str = ""; metadata: dict[str, Any] | None = None

class SourceAdapter:
    source_id = "unknown"; display_name = "Unknown"; timeout = 8
    def is_configured(self) -> bool: return True
    def search(self, claim: str) -> list[Evidence]: raise NotImplementedError
    def health_check(self) -> bool:
        try: self.search("test"); return True
        except Exception: return False
    def _get(self, url: str, **kwargs):
        response = requests.get(url, timeout=self.timeout, **kwargs); response.raise_for_status(); return response.json()
    def evidence(self, **kwargs) -> Evidence:
        return Evidence(retrieved_at=datetime.now(timezone.utc).isoformat(), **kwargs)
