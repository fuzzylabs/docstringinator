"""Factory for creating LLM providers."""

from typing import Any, Dict

from ..models import LLMProvider
from .anthropic import AnthropicProvider
from .base import LLMProviderBase
from .ollama import OllamaProvider
from .openai import OpenAIProvider


def create_llm_provider(provider: LLMProvider, config: Dict[str, Any]) -> LLMProviderBase:
    """Create an LLM provider instance.

    Args:
        provider: The LLM provider to use.
        config: Configuration for the provider.

    Returns:
        LLM provider instance.

    Raises:
        ValueError: If provider is not supported.
    """
    providers = {
        LLMProvider.OPENAI: OpenAIProvider,
        LLMProvider.ANTHROPIC: AnthropicProvider,
        LLMProvider.OLLAMA: OllamaProvider,
    }

    if provider not in providers:
        raise ValueError(f"Unsupported LLM provider: {provider}")

    return providers[provider](config)
