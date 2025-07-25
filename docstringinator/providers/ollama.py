"""Ollama LLM provider for Docstringinator."""

import asyncio
from typing import Any, Dict

import requests

from ..models import DocstringFormat, DocstringInfo
from .base import LLMProviderBase, LLMResponse


class OllamaProvider(LLMProviderBase):
    """Ollama LLM provider for local model inference."""

    def __init__(self, config: Dict[str, Any]):
        """Initialise Ollama provider.

        Args:
            config: Configuration for the provider.
        """
        super().__init__(config)
        self.base_url = config.get("base_url", "http://localhost:11434")
        self.model = config.get("model", "llama2")

        # Test connection to Ollama
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
        except requests.RequestException as e:
            raise ValueError(f"Cannot connect to Ollama at {self.base_url}: {e}")

    async def generate_docstring(
        self, docstring_info: DocstringInfo, format_style: DocstringFormat,
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
            # Use requests in a thread to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self._make_ollama_request,
                prompt,
            )

            return LLMResponse(
                content=response.get("response", ""),
                model=self.model,
                usage=response.get("usage"),
                finish_reason=(response.get("done", True) and "stop") or "length",
            )

        except Exception as e:
            raise RuntimeError(f"Ollama API error: {e}")

    def _make_ollama_request(self, prompt: str) -> Dict[str, Any]:
        """Make a request to Ollama API.

        Args:
            prompt: The prompt to send to the model.

        Returns:
            Response from Ollama API.
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens or 1000,
            },
        }

        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()
