"""OpenAI LLM provider for Docstringinator."""

from typing import Any, Dict

import openai

from ..models import DocstringFormat, DocstringInfo
from .base import LLMProviderBase, LLMResponse


class OpenAIProvider(LLMProviderBase):
    """OpenAI LLM provider."""

    def __init__(self, config: Dict[str, Any]):
        """Initialise OpenAI provider.

        Args:
            config: Configuration for the provider.
        """
        super().__init__(config)
        api_key = config.get("api_key")
        if not api_key:
            raise ValueError("OpenAI API key is required")

        self.client = openai.AsyncOpenAI(api_key=api_key)

    async def generate_docstring(
        self, docstring_info: DocstringInfo, format_style: DocstringFormat,
    ) -> LLMResponse:
        """Generate docstring using OpenAI.

        Args:
            docstring_info: Information about the function.
            format_style: The docstring format to use.

        Returns:
            Generated docstring response.
        """
        prompt = self._create_prompt(docstring_info, format_style)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a Python documentation expert."},
                    {"role": "user", "content": prompt},
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout,
            )

            return LLMResponse(
                content=response.choices[0].message.content or "",
                model=self.model,
                usage=response.usage.model_dump() if response.usage else None,
                finish_reason=response.choices[0].finish_reason,
            )

        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {e}")
