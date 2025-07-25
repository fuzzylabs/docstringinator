"""Utility functions for LLM providers."""

import asyncio

from ..models import DocstringFormat, DocstringInfo
from .base import LLMProviderBase, LLMResponse


async def generate_docstring_async(
    provider: LLMProviderBase, docstring_info: DocstringInfo, format_style: DocstringFormat,
) -> LLMResponse:
    """Generate a docstring asynchronously.

    Args:
        provider: LLM provider instance.
        docstring_info: Information about the function.
        format_style: The docstring format to use.

    Returns:
        Generated docstring response.
    """
    return await provider.generate_docstring(docstring_info, format_style)


def generate_docstring(
    provider: LLMProviderBase, docstring_info: DocstringInfo, format_style: DocstringFormat,
) -> LLMResponse:
    """Generate a docstring synchronously.

    Args:
        provider: LLM provider instance.
        docstring_info: Information about the function.
        format_style: The docstring format to use.

    Returns:
        Generated docstring response.
    """
    return asyncio.run(generate_docstring_async(provider, docstring_info, format_style))
