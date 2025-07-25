"""Docstringinator - A Python tool for automatically fixing and improving docstrings using LLMs."""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .config import Config
from .core import Docstringinator
from .models import Change, DocstringFormat

__all__ = [
    "Change",
    "Config",
    "DocstringFormat",
    "Docstringinator",
]
