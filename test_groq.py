"""Isolated check for loading the Groq configuration and contacting Groq."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# This is a manual connectivity script, not a pytest test.  Avoid a live API
# request merely because pytest imports files whose names begin with test_.
if "pytest" in sys.modules:
    import pytest
    pytest.skip("manual Groq connectivity check", allow_module_level=True)


def mask(value: str) -> str:
    """Display a key safely while retaining enough detail to identify it."""
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}{'*' * (len(value) - 8)}{value[-4:]}"


env_path = Path(__file__).resolve().parent / ".env"
loaded = load_dotenv(env_path, override=True)
api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

print(f".env location: {env_path}")
print(f".env loaded: {loaded}")
print(f"GROQ_API_KEY found: {api_key is not None and bool(api_key.strip())}")
print(f"GROQ_API_KEY (masked): {mask(api_key.strip()) if api_key and api_key.strip() else 'not set'}")
print(f"GROQ_MODEL: {model}")

if not api_key or not api_key.strip():
    print("Groq API key cannot be found: GROQ_API_KEY is absent or blank after loading .env.")
    sys.exit(1)

try:
    from groq import Groq

    client = Groq(api_key=api_key.strip())
    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "Hello"}],
    )
    print("Groq response:")
    print(completion.choices[0].message.content)
except Exception as exc:
    print("Groq API request failed:")
    print(f"{type(exc).__name__}: {exc}")
    raise
