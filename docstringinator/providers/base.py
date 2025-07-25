"""Base classes for LLM providers."""

import json
from abc import ABC, abstractmethod
from typing import Any, Dict

from pydantic import BaseModel

from ..models import DocstringFormat, DocstringInfo


class LLMResponse(BaseModel):
    """Response from an LLM provider."""

    content: str
    model: str
    usage: Dict[str, Any] = None
    finish_reason: str = None


class LLMProviderBase(ABC):
    """Base class for LLM providers."""

    def __init__(self, config: Dict[str, Any]):
        """Initialise the LLM provider.

        Args:
            config: Configuration for the provider.
        """
        self.config = config
        self.model = config.get("model", "gpt-4")
        self.temperature = config.get("temperature", 0.1)
        self.max_tokens = config.get("max_tokens")
        self.timeout = config.get("timeout", 30)

    @abstractmethod
    async def generate_docstring(
        self, docstring_info: DocstringInfo, format_style: DocstringFormat,
    ) -> LLMResponse:
        """Generate a docstring for the given function.

        Args:
            docstring_info: Information about the function.
            format_style: The docstring format to use.

        Returns:
            Generated docstring response.
        """

    def _create_prompt(self, docstring_info: DocstringInfo, format_style: DocstringFormat) -> str:
        """Create a prompt for docstring generation.

        Args:
            docstring_info: Information about the function.
            format_style: The docstring format to use.

        Returns:
            Formatted prompt string.
        """
        format_examples = {
            DocstringFormat.GOOGLE: self._get_google_example(),
            DocstringFormat.NUMPY: self._get_numpy_example(),
            DocstringFormat.RESTRUCTUREDTEXT: self._get_restructuredtext_example(),
        }

        example = format_examples.get(format_style, format_examples[DocstringFormat.GOOGLE])

        prompt = f"""You are a Python documentation expert. Generate a high-quality docstring for the following function using {format_style.value} style.

Function Information:
- Name: {docstring_info.function_name}
- Class: {docstring_info.class_name or 'N/A'}
- Module: {docstring_info.module_name}
- Signature: {docstring_info.signature}
- Return Type: {docstring_info.return_type or 'N/A'}
- Parameters: {json.dumps(docstring_info.parameters, indent=2)}
- Is Method: {docstring_info.is_method}
- Is Async: {docstring_info.is_async}

Example {format_style.value} style docstring:
{example}

Please generate a docstring for this function. The docstring should:
1. Clearly describe what the function does
2. Document all parameters with types and descriptions
3. Document the return value if applicable
4. Include examples if the function is simple enough
5. Document any exceptions that might be raised
6. Use proper British English spelling (e.g., 'analyse' not 'analyze', 'colour' not 'color')

Function to document:
```python
{docstring_info.signature}
```

Generate only the docstring content (without the triple quotes):"""

        return prompt

    def _get_google_example(self) -> str:
        """Get Google style docstring example.

        Returns:
            Example Google style docstring.
        """
        return '''def calculate_area(radius: float) -> float:
    """Calculate the area of a circle.
    
    Args:
        radius: The radius of the circle in metres.
        
    Returns:
        The area of the circle in square metres.
        
    Raises:
        ValueError: If radius is negative.
        
    Example:
        >>> calculate_area(5.0)
        78.53981633974483
    """'''

    def _get_numpy_example(self) -> str:
        """Get NumPy style docstring example.

        Returns:
            Example NumPy style docstring.
        """
        return '''def calculate_area(radius: float) -> float:
    """Calculate the area of a circle.
    
    Parameters
    ----------
    radius : float
        The radius of the circle in metres.
        
    Returns
    -------
    float
        The area of the circle in square metres.
        
    Raises
    ------
    ValueError
        If radius is negative.
        
    Examples
    --------
    >>> calculate_area(5.0)
    78.53981633974483
    """'''

    def _get_restructuredtext_example(self) -> str:
        """Get reStructuredText style docstring example.

        Returns:
            Example reStructuredText style docstring.
        """
        return '''def calculate_area(radius: float) -> float:
    """Calculate the area of a circle.
    
    :param radius: The radius of the circle in metres.
    :type radius: float
    :return: The area of the circle in square metres.
    :rtype: float
    :raises ValueError: If radius is negative.
    
    :Example:
    
    >>> calculate_area(5.0)
    78.53981633974483
    """'''
