"""Tests for Ollama LLM provider."""

from unittest.mock import Mock, patch

import pytest

from docstringinator.exceptions import APIError, DocstringinatorConnectionError
from docstringinator.models import DocstringFormat, DocstringInfo
from docstringinator.providers.ollama import OllamaProvider


class TestOllamaProvider:
    """Test the Ollama LLM provider."""

    @patch("requests.get")
    @patch("requests.post")
    def test_ollama_provider_initialisation(self, mock_get, _mock_post):
        """Test that OllamaProvider can be initialised."""
        # Mock successful connection test
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status.return_value = None

        config = {
            "model": "llama2",
            "base_url": "http://localhost:11434",
            "temperature": 0.1,
            "timeout": 30,
        }

        provider = OllamaProvider(config)
        assert provider.model == "llama2"
        assert provider.base_url == "http://localhost:11434"
        assert provider.temperature == 0.1

    @patch("requests.get")
    def test_ollama_provider_connection_failure(self, mock_get):
        """Test that OllamaProvider raises error on connection failure."""
        # Mock connection failure
        from requests import RequestException

        mock_get.side_effect = RequestException("Connection failed")

        config = {
            "model": "llama2",
            "base_url": "http://localhost:11434",
        }

        with pytest.raises(DocstringinatorConnectionError, match="Connection failed"):
            OllamaProvider(config)

    @patch("requests.get")
    @patch("requests.post")
    def test_ollama_generate_docstring(self, mock_post, mock_get):
        """Test docstring generation with Ollama."""
        # Mock successful connection test
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status.return_value = None

        # Mock successful API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": '"""Calculate the area of a circle.\n\nArgs:\n    radius: The radius of the circle.\n\nReturns:\n    The area of the circle.\n"""',
            "done": True,
            "usage": {"prompt_eval_count": 100, "eval_count": 50},
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        config = {
            "model": "llama2",
            "base_url": "http://localhost:11434",
            "temperature": 0.1,
            "timeout": 30,
        }

        provider = OllamaProvider(config)

        # Create a test docstring info
        docstring_info = DocstringInfo(
            function_name="calculate_area",
            class_name=None,
            module_name="test_module",
            signature="def calculate_area(radius: float) -> float:",
            existing_docstring=None,
            line_number=1,
            end_line_number=5,
            has_docstring=False,
            is_method=False,
            is_async=False,
            return_type="float",
            parameters=[{"name": "radius", "type": "float", "default": None}],
        )

        # Test synchronous generation
        response = provider.generate_docstring(docstring_info, DocstringFormat.GOOGLE)

        assert response.content is not None
        assert "Calculate the area" in response.content
        assert response.model == "llama2"
        assert response.finish_reason == "stop"

    @patch("requests.get")
    @patch("requests.post")
    def test_ollama_api_error(self, mock_post, mock_get):
        """Test handling of Ollama API errors."""
        # Mock successful connection test
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status.return_value = None

        # Mock API error
        mock_post.side_effect = Exception("API Error")

        config = {
            "model": "llama2",
            "base_url": "http://localhost:11434",
        }

        provider = OllamaProvider(config)

        docstring_info = DocstringInfo(
            function_name="test_function",
            class_name=None,
            module_name="test_module",
            signature="def test_function():",
            existing_docstring=None,
            line_number=1,
            end_line_number=3,
            has_docstring=False,
            is_method=False,
            is_async=False,
            return_type=None,
            parameters=[],
        )

        # Test that API errors are properly handled
        with pytest.raises(APIError, match="API error"):
            provider.generate_docstring(docstring_info, DocstringFormat.GOOGLE)

    @patch("requests.get")
    @patch("requests.post")
    def test_ollama_payload_structure(self, mock_post, mock_get):
        """Test that Ollama payload is correctly structured."""
        # Mock successful connection test
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status.return_value = None

        # Mock successful API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": "Test response",
            "done": True,
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        config = {
            "model": "llama2",
            "base_url": "http://localhost:11434",
            "temperature": 0.5,
            "max_tokens": 500,
        }

        provider = OllamaProvider(config)

        # Test the payload structure
        payload = provider._make_ollama_request("Test prompt")

        # Verify the method exists and returns expected structure
        assert hasattr(provider, "_make_ollama_request")
        assert callable(provider._make_ollama_request)
        assert payload["response"] == "Test response"
        assert payload["done"] is True
