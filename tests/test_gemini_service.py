from unittest.mock import Mock, patch

import pytest

from services.llm_service import GroqProvider, LLMServiceException


def test_groq_provider_uses_requested_model_and_extracts_text():
    fake_choice = Mock()
    fake_choice.message = Mock(content="Apple was founded by Steve Jobs.")

    fake_completion = Mock()
    fake_completion.choices = [fake_choice]

    fake_chat = Mock()
    fake_chat.completions.create.return_value = fake_completion

    fake_client = Mock()
    fake_client.chat = fake_chat

    with patch("services.llm_service.groq.Client", return_value=fake_client) as client_cls:
        result = GroqProvider("test-key").generate_response("Who founded Apple?")

    assert result == "Apple was founded by Steve Jobs."
    client_cls.assert_called_once()
    assert client_cls.call_args.kwargs["api_key"] == "test-key"
    fake_chat.completions.create.assert_called_once()
    assert fake_chat.completions.create.call_args.kwargs["model"] == "openai/gpt-oss-20b"
    assert fake_chat.completions.create.call_args.kwargs["messages"] == [
        {"role": "user", "content": "Who founded Apple?"}
    ]


def test_groq_provider_reports_network_failure():
    fake_chat = Mock()
    fake_chat.completions.create.side_effect = Exception("offline")

    fake_client = Mock()
    fake_client.chat = fake_chat

    with patch("services.llm_service.groq.Client", return_value=fake_client):
        with pytest.raises(LLMServiceException, match="offline"):
            GroqProvider("test-key").generate_response("Who founded Apple?")
