import pytest
from core.llm_client import LLMClient
from unittest.mock import patch, Mock

def test_generate_response():
    llm_client = LLMClient()
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        response = llm_client.generate_response("Test prompt")
        assert isinstance(response, str)
        assert response == "Test response"