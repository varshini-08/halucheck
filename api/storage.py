"""Small SQLite persistence layer for completed API analyses."""
import json, sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "results" / "halucheck_history.sqlite3"

def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.execute("CREATE TABLE IF NOT EXISTS analyses (id TEXT PRIMARY KEY, payload TEXT NOT NULL, created_at TEXT NOT NULL)")
    return con

def load_all() -> list[dict]:
    with _connect() as con:
        rows = con.execute("SELECT payload FROM analyses ORDER BY created_at DESC").fetchall()
    return [json.loads(row[0]) for row in rows]

def save(payload: dict) -> None:
    with _connect() as con:
        con.execute("INSERT OR REPLACE INTO analyses(id,payload,created_at) VALUES(?,?,?)", (payload["id"], json.dumps(payload), payload["timestamp"]))
