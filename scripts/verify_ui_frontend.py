"""Static checks for the HaluCheck Streamlit frontend.

Run from the repository root with: python scripts/verify_ui_frontend.py
This intentionally does not import app.py, because importing a Streamlit app
outside Streamlit can execute widgets and obscure the result of the check.
"""
from pathlib import Path
import ast
import json

ROOT = Path(__file__).resolve().parents[1]
app = ROOT / "app.py"
dashboard = ROOT / "visualization" / "dashboard.py"
legacy = ROOT / "app_new.py"

def function_line(path: Path, name: str) -> int | None:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    matches = [node.lineno for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name]
    return max(matches) if matches else None

checks = {
    "entrypoint_exists": app.exists(),
    "dashboard_exists": dashboard.exists(),
    "app_calls_dashboard_renderer": "dashboard.render_analysis(" in app.read_text(encoding="utf-8"),
    "new_dashboard_renderer_marker": "hc-page-heading" in dashboard.read_text(encoding="utf-8"),
    "legacy_entrypoint_is_not_primary": legacy.exists() and "legacy" in legacy.read_text(encoding="utf-8").lower(),
    "renderer_definition_line": function_line(dashboard, "render_analysis"),
}
checks["passed"] = all(value is not False and value is not None for value in checks.values())
print(json.dumps(checks, indent=2))
raise SystemExit(0 if checks["passed"] else 1)
