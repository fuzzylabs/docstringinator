"""Tests for Python parser functionality."""

from pathlib import Path

import pytest

from docstringinator.exceptions import ParseError
from docstringinator.parser import DocstringExtractor, PythonParser


class TestPythonParser:
    """Test the Python code parser."""

    def test_parse_string_simple_function(self):
        """Test parsing a simple function."""
        parser = PythonParser()
        code = """
def sample_function():
    pass
"""
        functions = parser.parse_string(code)

        assert len(functions) == 1
        func = functions[0]
        assert func.function_name == "sample_function"
        assert func.has_docstring is False

    def test_parse_string_function_with_docstring(self):
        """Test parsing a function with a docstring."""
        parser = PythonParser()
        code = """
def sample_function():
    \"\"\"This is a test function.\"\"\"
    pass
"""
        functions = parser.parse_string(code)

        assert len(functions) == 1
        func = functions[0]
        assert func.function_name == "sample_function"
        assert func.has_docstring is True
        assert func.existing_docstring == "This is a test function."

    def test_parse_string_function_with_parameters(self):
        """Test parsing a function with parameters."""
        parser = PythonParser()
        code = """
def sample_function(param1: str, param2: int = 10) -> bool:
    pass
"""
        functions = parser.parse_string(code)

        assert len(functions) == 1
        func = functions[0]
        assert func.function_name == "sample_function"
        assert len(func.parameters) == 2
        assert func.parameters[0]["name"] == "param1"
        assert func.parameters[0]["type"] == "str"
        assert func.parameters[1]["name"] == "param2"
        assert func.parameters[1]["type"] == "int"
        assert func.parameters[1]["default"] == "10"
        assert func.return_type == "bool"

    def test_parse_string_async_function(self):
        """Test parsing an async function."""
        parser = PythonParser()
        code = """
async def sample_async_function():
    pass
"""
        functions = parser.parse_string(code)

        assert len(functions) == 1
        func = functions[0]
        assert func.function_name == "sample_async_function"
        assert func.is_async is True

    def test_parse_string_class_method(self):
        """Test parsing a class method."""
        parser = PythonParser()
        code = """
class TestClass:
    def sample_method(self):
        pass
"""
        functions = parser.parse_string(code)

        assert len(functions) == 1
        func = functions[0]
        assert func.function_name == "sample_method"
        assert func.class_name == "TestClass"
        assert func.is_method is True

    def test_parse_string_skip_private_functions(self):
        """Test that private functions are skipped."""
        parser = PythonParser()
        code = """
def public_function():
    pass

def _private_function():
    pass

def __magic_function__():
    pass
"""
        functions = parser.parse_string(code)

        function_names = [f.function_name for f in functions]
        assert "public_function" in function_names
        assert "_private_function" not in function_names
        assert "__magic_function__" in function_names  # Magic methods are included

    def test_parse_string_skip_test_functions(self):
        """Test that test functions are skipped."""
        parser = PythonParser()
        code = """
def normal_function():
    pass

def test_function():
    pass

def test_something():
    pass
"""
        functions = parser.parse_string(code)

        function_names = [f.function_name for f in functions]
        assert "normal_function" in function_names
        assert "test_function" not in function_names
        assert "test_something" not in function_names

    def test_parse_file(self):
        """Test parsing a file."""
        parser = PythonParser()

        # Create a temporary file
        temp_file = Path("temp_test_file.py")
        temp_file.write_text(
            """
def sample_function():
    \"\"\"This is a test function.\"\"\"
    pass
""",
        )

        try:
            functions = parser.parse_file(str(temp_file))

            assert len(functions) == 1
            func = functions[0]
            assert func.function_name == "sample_function"
            assert func.module_name == "temp_test_file"
            assert func.has_docstring is True
        finally:
            temp_file.unlink(missing_ok=True)

    def test_parse_file_invalid_path(self):
        """Test parsing a non-existent file."""
        parser = PythonParser()

        with pytest.raises(ParseError):
            parser.parse_file("nonexistent_file.py")


class TestDocstringExtractor:
    """Test the docstring extractor."""

    def test_extract_docstrings(self):
        """Test extracting docstrings from a file."""
        extractor = DocstringExtractor()

        # Create a temporary file
        temp_file = Path("temp_test_file.py")
        temp_file.write_text(
            """
def function_with_docstring():
    \"\"\"This function has a docstring.\"\"\"
    pass

def function_without_docstring():
    pass
""",
        )

        try:
            functions = extractor.extract_docstrings(temp_file)

            assert len(functions) == 2

            # Check function with docstring
            func_with_doc = next(
                f for f in functions if f.function_name == "function_with_docstring"
            )
            assert func_with_doc.has_docstring is True
            assert func_with_doc.existing_docstring == "This function has a docstring."

            # Check function without docstring
            func_without_doc = next(
                f for f in functions if f.function_name == "function_without_docstring"
            )
            assert func_without_doc.has_docstring is False
            assert func_without_doc.existing_docstring is None
        finally:
            temp_file.unlink(missing_ok=True)

    def test_find_missing_docstrings(self):
        """Test finding functions without docstrings."""
        extractor = DocstringExtractor()

        # Create a temporary file
        temp_file = Path("temp_test_file.py")
        temp_file.write_text(
            """
def function_with_docstring():
    \"\"\"This function has a docstring.\"\"\"
    pass

def function_without_docstring():
    pass

def another_function():
    pass
""",
        )

        try:
            missing_docstrings = extractor.find_missing_docstrings(temp_file)

            assert len(missing_docstrings) == 2
            function_names = [f.function_name for f in missing_docstrings]
            assert "function_without_docstring" in function_names
            assert "another_function" in function_names
            assert "function_with_docstring" not in function_names
        finally:
            temp_file.unlink(missing_ok=True)

    def test_find_poor_docstrings(self):
        """Test finding functions with poor docstrings."""
        extractor = DocstringExtractor()

        # Create a temporary file
        temp_file = Path("temp_test_file.py")
        temp_file.write_text(
            """
def good_function():
    \"\"\"This is a good docstring with proper documentation.

    Args:
        param: A parameter.

    Returns:
        A value.
    \"\"\"
    pass

def poor_function():
    \"\"\"Short.\"\"\"
    pass

def another_poor_function():
    \"\"\"This docstring lacks proper structure.\"\"\"
    pass
""",
        )

        try:
            poor_docstrings = extractor.find_poor_docstrings(temp_file)

            assert len(poor_docstrings) == 2
            function_names = [f.function_name for f in poor_docstrings]
            assert "poor_function" in function_names
            assert "another_poor_function" in function_names
            assert "good_function" not in function_names
        finally:
            temp_file.unlink(missing_ok=True)

    def test_get_function_code(self):
        """Test getting function source code."""
        extractor = DocstringExtractor()

        # Create a temporary file
        temp_file = Path("temp_test_file.py")
        temp_file.write_text(
            """
def sample_function():
    \"\"\"This is a test function.\"\"\"
    return True
""",
        )

        try:
            code = extractor.get_function_code(temp_file, "sample_function")

            assert code is not None
            assert "def sample_function" in code
            assert "return True" in code
        finally:
            temp_file.unlink(missing_ok=True)

    def test_get_function_code_not_found(self):
        """Test getting code for non-existent function."""
        extractor = DocstringExtractor()

        # Create a temporary file
        temp_file = Path("temp_test_file.py")
        temp_file.write_text(
            """
def sample_function():
    pass
""",
        )

        try:
            code = extractor.get_function_code(temp_file, "nonexistent_function")

            assert code is None
        finally:
            temp_file.unlink(missing_ok=True)
