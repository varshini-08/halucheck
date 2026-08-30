import os

from utils.env_utils import load_environment


def test_load_environment_uses_explicit_env_file_and_overrides_blank_value(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("GEMINI_API_KEY=configured-key\n", encoding="utf-8")
    monkeypatch.setenv("GEMINI_API_KEY", "")

    load_environment(str(env_file))

    assert os.environ["GEMINI_API_KEY"] == "configured-key"
