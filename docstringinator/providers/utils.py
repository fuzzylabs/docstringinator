"""Utility functions for LLM providers."""

from docstringinator.models import DocstringFormat, DocstringInfo
from docstringinator.providers.base import LLMProviderBase, LLMResponse


def generate_docstring(
    provider: LLMProviderBase,
    docstring_info: DocstringInfo,
    format_style: DocstringFormat,
) -> LLMResponse:
    """Generate docstring using the provided provider.

    Args:
        provider: The LLM provider to use.
        docstring_info: Information about the function.
        format_style: The docstring format to use.

    Returns:
        Generated docstring response.
    """
    return provider.generate_docstring(docstring_info, format_style)
