"""Anthropic LLM provider for Docstringinator."""

from typing import Any, Dict

from anthropic import Anthropic

from docstringinator.exceptions import APIError, APIKeyRequiredError
from docstringinator.models import DocstringFormat, DocstringInfo
from docstringinator.providers.base import LLMProviderBase, LLMResponse


class AnthropicProvider(LLMProviderBase):
    """Anthropic LLM provider."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        api_key = config.get("api_key")
        if not api_key:
            raise APIKeyRequiredError
        self.client = Anthropic(api_key=api_key)

    def generate_docstring(
        self,
        docstring_info: DocstringInfo,
        format_style: DocstringFormat,
    ) -> LLMResponse:
        prompt = self._create_prompt(docstring_info, format_style)
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens or 1000,
                temperature=self.temperature,
                messages=[{"role": "user", "content": prompt}],
            )
            # Extract text content from the response
            content_text = ""
            if response.content and len(response.content) > 0:
                first_content = response.content[0]
                if hasattr(first_content, "text"):
                    content_text = first_content.text
                else:
                    # Handle other content types
                    content_text = str(first_content)

            return LLMResponse(
                content=content_text,
                model=self.model,
                usage=response.usage.model_dump() if response.usage else {},
                finish_reason=str(response.stop_reason),
            )
        except Exception as e:
            raise APIError from e
