"""Anthropic LLM provider for Docstringinator."""

from typing import Any, Dict

from anthropic import Anthropic

from ..models import DocstringFormat, DocstringInfo
from .base import LLMProviderBase, LLMResponse


class AnthropicProvider(LLMProviderBase):
    """Anthropic LLM provider."""

    def __init__(self, config: Dict[str, Any]):
        """Initialise Anthropic provider.

        Args:
            config: Configuration for the provider.
        """
        super().__init__(config)
        api_key = config.get("api_key")
        if not api_key:
            raise ValueError("Anthropic API key is required")

        self.client = Anthropic(api_key=api_key)

    async def generate_docstring(
        self, docstring_info: DocstringInfo, format_style: DocstringFormat,
    ) -> LLMResponse:
        """Generate docstring using Anthropic.

        Args:
            docstring_info: Information about the function.
            format_style: The docstring format to use.

        Returns:
            Generated docstring response.
        """
        prompt = self._create_prompt(docstring_info, format_style)

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens or 1000,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": prompt},
                ],
            )

            return LLMResponse(
                content=response.content[0].text,
                model=self.model,
                usage=response.usage.model_dump() if response.usage else None,
                finish_reason=response.stop_reason,
            )

        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {e}")
