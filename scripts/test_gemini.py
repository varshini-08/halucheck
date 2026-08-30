"""Opt-in Gemini connectivity check; never prints credentials."""
from __future__ import annotations
import os, time, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from services.gemini_service import GeminiProvider, GeminiServiceException

def main() -> int:
    configured = bool(os.environ.get("GEMINI_API_KEY", "").strip())
    if not configured:
        print("Gemini provider: BLOCKED\nAPI key configured: NO\nConnectivity: NOT RUN")
        return 1
    started=time.perf_counter()
    try:
        provider=GeminiProvider(); text=provider.generate_response("Reply with the single word OK.")
        print(f"Gemini provider: PASS\nModel: {provider.model}\nAPI key configured: YES\nConnectivity: PASS\nLatency: {time.perf_counter()-started:.3f} seconds\nResponse length: {len(text)}")
        return 0
    except Exception as exc:
        print(f"Gemini provider: FAIL\nAPI key configured: YES\nReason: {type(exc).__name__}: {str(exc)[:300]}")
        return 1
if __name__ == "__main__": raise SystemExit(main())
