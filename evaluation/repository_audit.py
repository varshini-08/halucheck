"""Repository validation and artifact inventory for Phase 6 packaging."""
from __future__ import annotations
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def audit(root: Path = ROOT) -> dict:
    ignored = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".test-tmp"}
    files = [p for p in root.rglob("*") if p.is_file() and not ignored.intersection(p.parts)]
    secret_matches = []
    for path in files:
        if path.suffix.lower() not in {".json", ".csv", ".md", ".log", ".txt"}:
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if re.search(r"(?i)(gsk_[A-Za-z0-9]{20,}|bearer\s+[A-Za-z0-9._-]+)", content):
            secret_matches.append(str(path.relative_to(root)))
    return {
        "source_files": sum(path.suffix == ".py" for path in files),
        "data_files": sum("data" in path.parts for path in files),
        "result_files": sum("results" in path.parts for path in files),
        "secret_pattern_matches": secret_matches,
        ".env_ignored": ".env" in (root / ".gitignore").read_text(encoding="utf-8"),
    }

if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
