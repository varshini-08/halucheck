"""Environment loading utilities for HaluCheck."""

from pathlib import Path

from dotenv import load_dotenv


def load_environment(env_path: str | None = None) -> None:
    """Load the project .env file, independent of the process working directory."""
    env_file = Path(env_path) if env_path else Path(__file__).resolve().parents[1] / ".env"
    if env_file.exists():
        load_dotenv(dotenv_path=env_file, override=True)
