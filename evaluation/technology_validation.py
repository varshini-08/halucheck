"""Capability checks that do not make external API calls or expose secrets."""
from __future__ import annotations
import importlib, json, os
from pathlib import Path
from services.config import CURRENT_RETRIEVAL_MODEL, PAPER_RETRIEVAL_MODEL

ROOT = Path(__file__).resolve().parents[1]

def check(name, module, critical, configured=None):
    try:
        imported = importlib.import_module(module)
        available = True; error = None; version = getattr(imported, "__version__", None)
    except Exception as exc:
        available = False; version = None; error = type(exc).__name__ + ": " + str(exc)
    return {"name": name, "module": module, "available": available, "version": version, "critical": critical, "configured": configured, "functional_test": "import only; live service/model test not invoked", "error": error}

def validate(output: str | Path = "results/final_validation/technology_validation.json"):
    checks = [
        check("Groq", "groq", True, os.environ.get("GROQ_MODEL", "openai/gpt-oss-20b")),
        check("spaCy", "spacy", True, "en_core_web_sm"),
        check("RapidFuzz", "rapidfuzz", True),
        check("SentenceTransformers", "sentence_transformers", True, CURRENT_RETRIEVAL_MODEL),
        check("FAISS", "faiss", True),
        check("Requests", "requests", True),
        check("Transformers", "transformers", True, "MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli"),
        check("Torch", "torch", True),
        check("Streamlit", "streamlit", True),
    ]
    result = {"checks": checks, "production_retrieval_model": CURRENT_RETRIEVAL_MODEL, "optional_paper_retrieval_model": PAPER_RETRIEVAL_MODEL, "groq_key_configured": bool(os.environ.get("GROQ_API_KEY")), "external_live_calls": False}
    path = ROOT / output; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(result, indent=2), encoding="utf-8"); return result

if __name__ == "__main__": print(json.dumps(validate(), indent=2))
