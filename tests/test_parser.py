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


class TestDocstringPlacement:
    """Test docstring placement functionality."""

    def test_simple_function_line_numbers(self):
        """Test that parser returns correct line numbers for simple functions."""
        parser = PythonParser()
        code = """def simple_function():
    return True

def another_function():
    return False
"""
        functions = parser.parse_string(code)

        # Check that parser returns correct line numbers
        assert functions[0].function_name == "simple_function"
        assert functions[0].line_number == 1  # Should be line 1 (where colon is)

        assert functions[1].function_name == "another_function"
        assert functions[1].line_number == 4  # Should be line 4 (where colon is)

    def test_multi_line_function_line_numbers(self):
        """Test that parser returns correct line numbers for multi-line functions."""
        parser = PythonParser()
        code = """def multi_line_function(
    param1: str,
    param2: int = 10,
    param3: list = None
) -> dict:
    return {"param1": param1, "param2": param2, "param3": param3}
"""
        functions = parser.parse_string(code)

        # Check that parser returns correct line number for multi-line function
        assert functions[0].function_name == "multi_line_function"
        assert functions[0].line_number == 5  # Should be line 5 (where colon is)

    def test_complex_function_line_numbers(self):
        """Test that parser returns correct line numbers for complex functions."""
        parser = PythonParser()
        code = """def very_long_function_signature(
    first_parameter: str,
    second_parameter: int,
    third_parameter: list,
    fourth_parameter: dict,
    fifth_parameter: bool = True,
    sixth_parameter: float = 0.0
) -> tuple:
    return (first_parameter, second_parameter, third_parameter)
"""
        functions = parser.parse_string(code)

        # Check that parser returns correct line number for complex function
        assert functions[0].function_name == "very_long_function_signature"
        assert functions[0].line_number == 8  # Should be line 8 (where colon is)

    def test_class_method_line_numbers(self):
        """Test that parser returns correct line numbers for class methods."""
        parser = PythonParser()
        code = """class TestClass:
    def __init__(self, value: int = 0):
        self.value = value

    def method_with_multi_line_signature(
        self,
        param1: str,
        param2: int,
        param3: list = None
    ) -> str:
        return f"{param1}: {param2}"
"""
        functions = parser.parse_string(code)

        # Check that parser returns correct line numbers for class methods
        assert functions[0].function_name == "__init__"
        assert functions[0].line_number == 2  # Should be line 2 (where colon is)

        assert functions[1].function_name == "method_with_multi_line_signature"
        assert functions[1].line_number == 10  # Should be line 10 (where colon is)

    def test_multiple_functions_mixed_types(self):
        """Test that parser handles multiple functions of different types correctly."""
        parser = PythonParser()
        code = """def simple_function():
    return True

def multi_line_function(
    param1: str,
    param2: int = 10,
    param3: list = None
) -> dict:
    return {"param1": param1, "param2": param2, "param3": param3}

def complex_function(
    first_param: str,
    second_param: int,
    third_param: list,
    fourth_param: dict,
    fifth_param: bool = True,
    sixth_param: float = 0.0
) -> tuple:
    return (first_param, second_param, third_param)

class TestClass:
    def __init__(self, value: int = 0):
        self.value = value

    def method_with_params(
        self,
        param1: str,
        param2: int,
        param3: list = None
    ) -> str:
        return f"{param1}: {param2}"

def final_function():
    return "done"
"""
        functions = parser.parse_string(code)

        # Check that all functions are parsed correctly
        assert len(functions) == 6

        # Check simple function
        simple_func = next(f for f in functions if f.function_name == "simple_function")
        assert simple_func.line_number == 1

        # Check multi-line function
        multi_func = next(
            f for f in functions if f.function_name == "multi_line_function"
        )
        assert multi_func.line_number == 8

        # Check complex function
        complex_func = next(
            f for f in functions if f.function_name == "complex_function"
        )
        assert complex_func.line_number == 18

        # Check class methods
        init_func = next(f for f in functions if f.function_name == "__init__")
        assert init_func.line_number == 22
        assert init_func.class_name == "TestClass"

        method_func = next(
            f for f in functions if f.function_name == "method_with_params"
        )
        assert method_func.line_number == 30
        assert method_func.class_name == "TestClass"

        # Check final function
        final_func = next(f for f in functions if f.function_name == "final_function")
        assert final_func.line_number == 33

    def test_function_with_comments_and_whitespace(self):
        """Test that parser handles functions with comments and whitespace correctly."""
        parser = PythonParser()
        code = """# This is a comment
def function_with_comments(
    # Parameter comment
    param1: str,
    param2: int = 10,  # Default value comment
    param3: list = None
) -> dict:  # Return type comment
    # Function body comment
    return {"param1": param1, "param2": param2, "param3": param3}

# Another comment
def another_function():
    return False
"""
        functions = parser.parse_string(code)

        # Check that functions are parsed correctly despite comments
        assert len(functions) == 2

        # Check first function
        first_func = next(
            f for f in functions if f.function_name == "function_with_comments"
        )
        assert first_func.line_number == 7  # Where the colon is

        # Check second function
        second_func = next(
            f for f in functions if f.function_name == "another_function"
        )
        assert second_func.line_number == 12  # Where the colon is

    def test_nested_functions_and_classes(self):
        """Test that parser handles nested functions and classes correctly."""
        parser = PythonParser()
        code = """def outer_function():
    def inner_function():
        return "inner"
    return "outer"

class OuterClass:
    def outer_method(self):
        def inner_method():
            return "inner"
        return "outer"

def standalone_function():
    return "standalone"
"""
        functions = parser.parse_string(code)

        # All functions should be parsed (including nested ones)
        assert len(functions) == 5

        # Check outer function
        outer_func = next(f for f in functions if f.function_name == "outer_function")
        assert outer_func.line_number == 1

        # Check inner function (nested)
        inner_func = next(f for f in functions if f.function_name == "inner_function")
        assert inner_func.line_number == 2

        # Check outer method
        outer_method = next(f for f in functions if f.function_name == "outer_method")
        assert outer_method.line_number == 7
        assert outer_method.class_name == "OuterClass"

        # Check inner method (nested)
        inner_method = next(f for f in functions if f.function_name == "inner_method")
        assert inner_method.line_number == 8

        # Check standalone function
        standalone_func = next(
            f for f in functions if f.function_name == "standalone_function"
        )
        assert standalone_func.line_number == 12
