"""Factory for creating LLM providers."""

from typing import Any, Dict

from docstringinator.exceptions import UnsupportedProviderError
from docstringinator.models import LLMProvider
from docstringinator.providers.anthropic import AnthropicProvider
from docstringinator.providers.base import LLMProviderBase
from docstringinator.providers.ollama import OllamaProvider
from docstringinator.providers.openai import OpenAIProvider


def create_llm_provider(
    provider: LLMProvider,
    config: Dict[str, Any],
) -> LLMProviderBase:
    providers = {
        LLMProvider.OPENAI: OpenAIProvider,
        LLMProvider.ANTHROPIC: AnthropicProvider,
        LLMProvider.OLLAMA: OllamaProvider,
    }
    if provider not in providers:
        raise UnsupportedProviderError(provider)
    return providers[provider](config)
