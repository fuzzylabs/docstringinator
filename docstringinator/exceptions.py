"""Custom exceptions for Docstringinator."""


class DocstringinatorError(Exception):
    """Base exception for Docstringinator."""


class ConfigurationError(DocstringinatorError):
    """Raised when there's a configuration error."""


class InvalidYAMLError(ConfigurationError):
    """Raised when YAML configuration is invalid."""

    def __init__(self, path: str):
        super().__init__(f"Invalid YAML in config file: {path}")
        self.path = path


class InvalidConfigurationError(ConfigurationError):
    """Raised when configuration is invalid."""

    def __init__(self, path: str):
        super().__init__(f"Invalid configuration: {path}")
        self.path = path


class APIKeyRequiredError(ConfigurationError):
    """Raised when API key is required but not provided."""

    def __init__(self, provider: str = "unknown"):
        super().__init__(f"API key required for provider: {provider}")
        self.provider = provider


class OllamaConnectionError(ConfigurationError):
    """Raised when Ollama connection fails."""

    def __init__(self, base_url: str):
        super().__init__(f"Ollama connection failed: {base_url}")
        self.base_url = base_url


class InvalidFileSizeError(ConfigurationError):
    """Raised when file size is invalid."""

    def __init__(self, size: int):
        super().__init__(f"Invalid file size: {size}")
        self.size = size


class InvalidTemperatureError(ConfigurationError):
    """Raised when temperature is invalid."""

    def __init__(self, temperature: float):
        super().__init__(f"Invalid temperature: {temperature}")
        self.temperature = temperature


class InvalidLineLengthError(ConfigurationError):
    """Raised when line length is invalid."""

    def __init__(self, length: int):
        super().__init__(f"Invalid line length: {length}")
        self.length = length


class ProcessingError(DocstringinatorError):
    """Raised when file processing fails."""

    def __init__(self) -> None:
        super().__init__("Processing failed.")


class ParseError(DocstringinatorError):
    """Raised when parsing fails."""

    def __init__(self) -> None:
        super().__init__("Parse failed.")


class APIError(DocstringinatorError):
    """Raised when API calls fail."""

    def __init__(self) -> None:
        super().__init__("API error.")


class UnsupportedProviderError(DocstringinatorError):
    """Raised when LLM provider is not supported."""

    def __init__(self, provider: str):
        super().__init__(f"Unsupported provider: {provider}")
        self.provider = provider


class DocstringinatorConnectionError(DocstringinatorError):
    """Raised when connection fails."""

    def __init__(self, base_url: str):
        super().__init__(f"Connection failed: {base_url}")
        self.base_url = base_url
