"""Ollama LLM provider for Docstringinator."""

from typing import Any, Dict

import requests

from docstringinator.exceptions import APIError, DocstringinatorConnectionError
from docstringinator.models import DocstringFormat, DocstringInfo
from docstringinator.providers.base import LLMProviderBase, LLMResponse


class OllamaProvider(LLMProviderBase):
    """Ollama LLM provider for local model inference."""

    def __init__(self, config: Dict[str, Any]):
        """Initialise Ollama provider.

        Args:
            config: Configuration for the provider.
        """
        super().__init__(config)
        self.model = config.get("model", "llama2")
        self.base_url = config.get("ollama_base_url", "http://localhost:11434")
        self.temperature = config.get("temperature", 0.1)
        self.max_tokens = config.get("max_tokens", 1024)
        self.timeout = config.get("timeout", 30)
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=3)
            response.raise_for_status()
        except requests.RequestException as e:
            raise DocstringinatorConnectionError(self.base_url) from e

    def generate_docstring(
        self,
        docstring_info: DocstringInfo,
        format_style: DocstringFormat,
    ) -> LLMResponse:
        """Generate docstring using Ollama.

        Args:
            docstring_info: Information about the function.
            format_style: The docstring format to use.

        Returns:
            Generated docstring response.
        """
        prompt = self._create_prompt(docstring_info, format_style)

        try:
            response = self._make_ollama_request(prompt)

            return LLMResponse(
                content=response.get("response", ""),
                model=self.model,
                usage=response.get("usage") or {},
                finish_reason=(response.get("done", True) and "stop") or "length",
            )

        except Exception as e:
            raise APIError from e

    def _make_ollama_request(self, prompt: str) -> Dict[str, Any]:
        """Make a request to Ollama API.

        Args:
            prompt: The prompt to send to the model.

        Returns:
            Response from Ollama API.
        """
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
            },
        }

        response = requests.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        return response.json()  # type: ignore
