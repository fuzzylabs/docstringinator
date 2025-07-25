"""Base classes for LLM providers."""

from abc import ABC, abstractmethod
from typing import Any, Dict

from pydantic import BaseModel

from docstringinator.models import DocstringFormat, DocstringInfo


class LLMResponse(BaseModel):
    """Response from an LLM provider."""

    content: str
    model: str
    usage: Dict[str, Any] = {}
    finish_reason: str = ""


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
    def generate_docstring(
        self,
        docstring_info: DocstringInfo,
        format_style: DocstringFormat,
    ) -> LLMResponse:
        """Generate a docstring for the given function.

        Args:
            docstring_info: Information about the function.
            format_style: The docstring format to use.

        Returns:
            Generated docstring response.
        """

    def _create_prompt(
        self,
        docstring_info: DocstringInfo,
        format_style: DocstringFormat,
    ) -> str:
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

        example = format_examples.get(
            format_style,
            format_examples[DocstringFormat.GOOGLE],
        )

        # Build context about the function
        context_parts = []
        if docstring_info.class_name:
            context_parts.append(
                f"This is a method of the {docstring_info.class_name} class.",
            )
        if docstring_info.is_async:
            context_parts.append("This is an async function.")
        if docstring_info.function_name.startswith(
            "__",
        ) and docstring_info.function_name.endswith("__"):
            context_parts.append("This is a special/magic method.")

        context = (
            " ".join(context_parts) if context_parts else "This is a regular function."
        )

        # Format parameters for better readability
        param_descriptions = []
        if docstring_info.parameters:
            for param in docstring_info.parameters:
                param_str = f"  - {param['name']}: {param['type']}"
                if not param.get("required", True):
                    param_str += f" (optional, default: {param.get('default', 'None')})"
                param_descriptions.append(param_str)

        param_info = (
            "\n".join(param_descriptions) if param_descriptions else "  - No parameters"
        )

        # Determine what sections to include based on function characteristics
        has_parameters = bool(docstring_info.parameters)
        has_return_type = bool(
            docstring_info.return_type and docstring_info.return_type.lower() != "none",
        )
        has_function_body = bool(
            docstring_info.function_body and docstring_info.function_body.strip(),
        )

        # Check if function body suggests it might raise exceptions
        might_raise_exceptions = False
        if has_function_body:
            body_lower = docstring_info.function_body.lower()
            might_raise_exceptions = any(
                keyword in body_lower
                for keyword in [
                    "raise",
                    "except",
                    "error",
                    "assert",
                    "if ",
                    "validation",
                    "check",
                ]
            )

        return f"""You are an expert Python developer. Write a concise, accurate docstring for this function.

FUNCTION:
{docstring_info.signature}

FUNCTION BODY:
{docstring_info.function_body or "# Function body not available"}

ANALYSIS:
- Function name: {docstring_info.function_name}
- {context}
- Has parameters: {has_parameters}
- Returns: {docstring_info.return_type or 'None/unspecified'}
- Might raise exceptions: {might_raise_exceptions}

REQUIREMENTS:
1. Write ONLY the docstring content (no triple quotes)
2. Start with a brief, clear description of what the function does (analyze the actual code)
3. Be concise - avoid unnecessary words like "This function"
4. ONLY include sections that are relevant:
   - Include Args section ONLY if function has parameters
   - Include Returns section ONLY if function returns something meaningful (not None)
   - Include Raises section ONLY if function might raise exceptions (has conditionals, validations, etc.)
5. Use {format_style.value} format
6. Keep descriptions short and precise

STYLE EXAMPLE:
{example}

ANALYSIS GUIDELINES:
- Look at the function body to understand what it actually does
- For simple functions that just return a value, keep the description very brief
- Don't include empty or placeholder sections
- Focus on the function's purpose, not implementation details

Generate a concise docstring:"""

    def _get_google_example(self) -> str:
        """Get Google style docstring example.

        Returns:
            Example Google style docstring.
        """
        return '''def calculate_area(radius: float) -> float:
    """Calculate the area of a circle.

    Args:
        radius: The radius of the circle in meters.

    Returns:
        The area in square meters.

    Raises:
        ValueError: If radius is negative.
    """'''

    def _get_numpy_example(self) -> str:
        """Get NumPy style docstring example.

        Returns:
            Example NumPy style docstring.
        """
        return '''def calculate_area(radius: float) -> float:
    """
    Calculate the area of a circle.

    Parameters
    ----------
    radius : float
        The radius of the circle in meters.

    Returns
    -------
    float
        The area in square meters.

    Raises
    ------
    ValueError
        If radius is negative.
    """'''

    def _get_restructuredtext_example(self) -> str:
        """Get reStructuredText style docstring example.

        Returns:
            Example reStructuredText style docstring.
        """
        return '''def calculate_area(radius: float) -> float:
    """
    Calculate the area of a circle.

    :param radius: The radius of the circle in meters.
    :type radius: float
    :returns: The area in square meters.
    :rtype: float
    :raises ValueError: If radius is negative.
    """'''
