"""Tests for core Docstringinator functionality."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from docstringinator.core import Docstringinator
from docstringinator.models import (
    BatchResult,
    Config,
    LLMConfig,
    LLMProvider,
    ProcessingResult,
)


class TestDocstringinator:
    """Test the main Docstringinator class."""

    @patch("docstringinator.core.create_llm_provider")
    @patch("docstringinator.core.load_config")
    @patch("docstringinator.core.validate_config")
    def test_initialisation(
        self,
        mock_validate_config,
        mock_load_config,
        mock_create_llm,
    ):
        """Test that Docstringinator can be initialised."""
        # Mock the configuration
        mock_config = Config(
            llm=LLMConfig(
                provider=LLMProvider.LOCAL,
                model="test-model",
                api_key="test-key",
                temperature=0.1,
            ),
        )
        mock_load_config.return_value = mock_config

        # Mock the LLM provider
        mock_llm_provider = Mock()
        mock_create_llm.return_value = mock_llm_provider

        docstringinator = Docstringinator()
        assert docstringinator is not None
        assert hasattr(docstringinator, "config")
        assert hasattr(docstringinator, "llm_provider")
        assert hasattr(docstringinator, "extractor")

    @patch("docstringinator.core.create_llm_provider")
    @patch("docstringinator.core.load_config")
    @patch("docstringinator.core.validate_config")
    def test_fix_file_with_invalid_path(
        self,
        mock_validate_config,
        mock_load_config,
        mock_create_llm,
    ):
        """Test that invalid file paths raise appropriate errors."""
        # Mock the configuration
        mock_config = Config(
            llm=LLMConfig(
                provider=LLMProvider.LOCAL,
                model="test-model",
                api_key="test-key",
                temperature=0.1,
            ),
        )
        mock_load_config.return_value = mock_config

        # Mock the LLM provider
        mock_llm_provider = Mock()
        mock_create_llm.return_value = mock_llm_provider

        docstringinator = Docstringinator()

        with pytest.raises(FileNotFoundError):
            docstringinator.fix_file("nonexistent_file.py")

    @patch("docstringinator.core.create_llm_provider")
    @patch("docstringinator.core.load_config")
    @patch("docstringinator.core.validate_config")
    def test_fix_file_with_non_python_file(
        self,
        mock_validate_config,
        mock_load_config,
        mock_create_llm,
    ):
        """Test that non-Python files raise appropriate errors."""
        # Mock the configuration
        mock_config = Config(
            llm=LLMConfig(
                provider=LLMProvider.LOCAL,
                model="test-model",
                api_key="test-key",
                temperature=0.1,
            ),
        )
        mock_load_config.return_value = mock_config

        # Mock the LLM provider
        mock_llm_provider = Mock()
        mock_create_llm.return_value = mock_llm_provider

        docstringinator = Docstringinator()

        # Create a temporary non-Python file
        temp_file = Path("temp_test_file.txt")
        temp_file.write_text("This is not a Python file")

        try:
            with pytest.raises(ValueError):
                docstringinator.fix_file(str(temp_file))
        finally:
            temp_file.unlink(missing_ok=True)

    @patch("docstringinator.core.create_llm_provider")
    @patch("docstringinator.core.load_config")
    @patch("docstringinator.core.validate_config")
    def test_fix_directory_with_invalid_path(
        self,
        mock_validate_config,
        mock_load_config,
        mock_create_llm,
    ):
        """Test that invalid directory paths raise appropriate errors."""
        # Mock the configuration
        mock_config = Config(
            llm=LLMConfig(
                provider=LLMProvider.LOCAL,
                model="test-model",
                api_key="test-key",
                temperature=0.1,
            ),
        )
        mock_load_config.return_value = mock_config

        # Mock the LLM provider
        mock_llm_provider = Mock()
        mock_create_llm.return_value = mock_llm_provider

        docstringinator = Docstringinator()

        with pytest.raises(FileNotFoundError):
            docstringinator.fix_directory("nonexistent_directory")

    @patch("docstringinator.core.create_llm_provider")
    @patch("docstringinator.core.load_config")
    @patch("docstringinator.core.validate_config")
    def test_fix_directory_with_file_path(
        self,
        mock_validate_config,
        mock_load_config,
        mock_create_llm,
    ):
        """Test that file paths passed to fix_directory raise appropriate errors."""
        # Mock the configuration
        mock_config = Config(
            llm=LLMConfig(
                provider=LLMProvider.LOCAL,
                model="test-model",
                api_key="test-key",
                temperature=0.1,
            ),
        )
        mock_load_config.return_value = mock_config

        # Mock the LLM provider
        mock_llm_provider = Mock()
        mock_create_llm.return_value = mock_llm_provider

        docstringinator = Docstringinator()

        # Create a temporary file
        temp_file = Path("temp_test_file.py")
        temp_file.write_text("def test(): pass")

        try:
            with pytest.raises(NotADirectoryError):
                docstringinator.fix_directory(str(temp_file))
        finally:
            temp_file.unlink(missing_ok=True)

    @patch("docstringinator.core.Docstringinator._process_file")
    @patch("docstringinator.core.create_llm_provider")
    @patch("docstringinator.core.load_config")
    @patch("docstringinator.core.validate_config")
    def test_fix_file_success(
        self,
        mock_validate_config,
        mock_load_config,
        mock_create_llm,
        mock_process_file,
    ):
        """Test successful file processing."""
        # Mock the configuration
        mock_config = Config(
            llm=LLMConfig(
                provider=LLMProvider.LOCAL,
                model="test-model",
                api_key="test-key",
                temperature=0.1,
            ),
        )
        mock_load_config.return_value = mock_config

        # Mock the LLM provider
        mock_llm_provider = Mock()
        mock_create_llm.return_value = mock_llm_provider

        # Create a temporary file
        temp_file = Path("temp_test_file.py")
        temp_file.write_text("def test(): pass")

        # Mock the processing result
        mock_result = ProcessingResult(
            file_path=temp_file,
            changes=[],
            errors=[],
            warnings=[],
            success=True,
            file_size=100,
            processing_time=1.0,
            docstrings_found=1,
            docstrings_modified=0,
            docstrings_added=0,
        )
        mock_process_file.return_value = mock_result

        try:
            docstringinator = Docstringinator()
            result = docstringinator.fix_file(str(temp_file))

            assert result.success is True
            assert result.file_path == temp_file
            mock_process_file.assert_called_once_with(temp_file)
        finally:
            temp_file.unlink(missing_ok=True)

    @patch("docstringinator.core.Docstringinator._process_directory")
    @patch("docstringinator.core.create_llm_provider")
    @patch("docstringinator.core.load_config")
    @patch("docstringinator.core.validate_config")
    def test_fix_directory_success(
        self,
        mock_validate_config,
        mock_load_config,
        mock_create_llm,
        mock_process_directory,
    ):
        """Test successful directory processing."""
        # Mock the configuration
        mock_config = Config(
            llm=LLMConfig(
                provider=LLMProvider.LOCAL,
                model="test-model",
                api_key="test-key",
                temperature=0.1,
            ),
        )
        mock_load_config.return_value = mock_config

        # Mock the LLM provider
        mock_llm_provider = Mock()
        mock_create_llm.return_value = mock_llm_provider

        # Create a temporary directory
        temp_dir = Path("temp_test_dir")
        temp_dir.mkdir(exist_ok=True)

        # Mock the processing result
        mock_result = BatchResult(
            total_files=1,
            successful_files=1,
            failed_files=0,
            total_changes=0,
            total_errors=0,
            total_warnings=0,
            total_processing_time=1.0,
            results=[],
        )
        mock_process_directory.return_value = mock_result

        try:
            docstringinator = Docstringinator()
            result = docstringinator.fix_directory(str(temp_dir))

            assert result.successful_files == 1
            assert result.failed_files == 0
            mock_process_directory.assert_called_once_with(temp_dir)
        finally:
            # Clean up
            for file in temp_dir.iterdir():
                file.unlink()
            temp_dir.rmdir()

    @patch("docstringinator.core.create_llm_provider")
    @patch("docstringinator.core.load_config")
    @patch("docstringinator.core.validate_config")
    def test_preview_changes(
        self,
        mock_validate_config,
        mock_load_config,
        mock_create_llm,
    ):
        """Test preview_changes method."""
        # Mock the configuration
        mock_config = Config(
            llm=LLMConfig(
                provider=LLMProvider.LOCAL,
                model="test-model",
                api_key="test-key",
                temperature=0.1,
            ),
        )
        mock_load_config.return_value = mock_config

        # Mock the LLM provider
        from docstringinator.providers.base import LLMResponse

        mock_llm_provider = Mock()
        mock_response = LLMResponse(
            content="Test docstring",
            model="test-model",
            usage={},
            finish_reason="stop",
        )
        mock_llm_provider.generate_docstring.return_value = mock_response
        mock_create_llm.return_value = mock_llm_provider

        docstringinator = Docstringinator()

        # Create a temporary file
        temp_file = Path("temp_test_file.py")
        temp_file.write_text("def test(): pass")

        try:
            changes = docstringinator.preview_changes(str(temp_file))
            assert isinstance(changes, list)
        finally:
            temp_file.unlink(missing_ok=True)

    @patch("docstringinator.core.create_llm_provider")
    @patch("docstringinator.core.load_config")
    @patch("docstringinator.core.validate_config")
    def test_fix_string(
        self,
        mock_validate_config,
        mock_load_config,
        mock_create_llm,
    ):
        """Test fix_string method."""
        # Mock the configuration
        mock_config = Config(
            llm=LLMConfig(
                provider=LLMProvider.LOCAL,
                model="test-model",
                api_key="test-key",
                temperature=0.1,
            ),
        )
        mock_load_config.return_value = mock_config

        # Mock the LLM provider
        mock_llm_provider = Mock()
        mock_create_llm.return_value = mock_llm_provider

        docstringinator = Docstringinator()

        code = "def test_function(): pass"
        result = docstringinator.fix_string(code)

        assert isinstance(result, str)
        assert "def test_function" in result

    @patch("docstringinator.core.create_llm_provider")
    @patch("docstringinator.core.load_config")
    @patch("docstringinator.core.validate_config")
    def test_should_improve_docstring(
        self,
        mock_validate_config,
        mock_load_config,
        mock_create_llm,
    ):
        """Test _should_improve_docstring method."""
        # Mock the configuration
        mock_config = Config(
            llm=LLMConfig(
                provider=LLMProvider.LOCAL,
                model="test-model",
                api_key="test-key",
                temperature=0.1,
            ),
        )
        mock_load_config.return_value = mock_config

        # Mock the LLM provider
        mock_llm_provider = Mock()
        mock_create_llm.return_value = mock_llm_provider

        docstringinator = Docstringinator()

        # Test with function that has no docstring
        from docstringinator.models import DocstringInfo

        func_no_docstring = DocstringInfo(
            function_name="test_func",
            class_name=None,
            module_name="test_module",
            signature="def test_func()",
            existing_docstring=None,
            line_number=1,
            end_line_number=3,
            has_docstring=False,
            is_method=False,
            is_async=False,
            return_type=None,
            parameters=[],
        )

        assert docstringinator._should_improve_docstring(func_no_docstring) is False

        # Test with function that has poor docstring
        func_poor_docstring = DocstringInfo(
            function_name="test_func",
            class_name=None,
            module_name="test_module",
            signature="def test_func()",
            existing_docstring="Short",
            line_number=1,
            end_line_number=3,
            has_docstring=True,
            is_method=False,
            is_async=False,
            return_type=None,
            parameters=[],
        )

        assert docstringinator._should_improve_docstring(func_poor_docstring) is True

    @patch("docstringinator.core.create_llm_provider")
    @patch("docstringinator.core.load_config")
    @patch("docstringinator.core.validate_config")
    def test_print_results(
        self,
        mock_validate_config,
        mock_load_config,
        mock_create_llm,
    ):
        """Test print_results method."""
        # Mock the configuration
        mock_config = Config(
            llm=LLMConfig(
                provider=LLMProvider.LOCAL,
                model="test-model",
                api_key="test-key",
                temperature=0.1,
            ),
        )
        mock_load_config.return_value = mock_config

        # Mock the LLM provider
        mock_llm_provider = Mock()
        mock_create_llm.return_value = mock_llm_provider

        docstringinator = Docstringinator()

        result = ProcessingResult(
            file_path=Path("test.py"),
            changes=[],
            errors=[],
            warnings=[],
            success=True,
            file_size=100,
            processing_time=1.0,
            docstrings_found=1,
            docstrings_modified=0,
            docstrings_added=0,
        )

        # Should not raise any exceptions
        docstringinator.print_results(result)

    @patch("docstringinator.core.create_llm_provider")
    @patch("docstringinator.core.load_config")
    @patch("docstringinator.core.validate_config")
    def test_print_batch_results(
        self,
        mock_validate_config,
        mock_load_config,
        mock_create_llm,
    ):
        """Test print_batch_results method."""
        # Mock the configuration
        mock_config = Config(
            llm=LLMConfig(
                provider=LLMProvider.LOCAL,
                model="test-model",
                api_key="test-key",
                temperature=0.1,
            ),
        )
        mock_load_config.return_value = mock_config

        # Mock the LLM provider
        mock_llm_provider = Mock()
        mock_create_llm.return_value = mock_llm_provider

        docstringinator = Docstringinator()

        result = BatchResult(
            total_files=1,
            successful_files=1,
            failed_files=0,
            total_changes=0,
            total_errors=0,
            total_warnings=0,
            total_processing_time=1.0,
            results=[],
        )

        # Should not raise any exceptions
        docstringinator.print_batch_results(result)

    @patch("docstringinator.core.create_llm_provider")
    @patch("docstringinator.core.load_config")
    @patch("docstringinator.core.validate_config")
    def test_clean_docstring(
        self, mock_validate_config, mock_load_config, mock_create_llm,
    ):
        """Test docstring cleanup functionality."""
        # Mock the configuration
        mock_config = Config(
            llm=LLMConfig(
                provider=LLMProvider.LOCAL,
                model="test-model",
                api_key="test-key",
                temperature=0.1,
            ),
        )
        mock_load_config.return_value = mock_config

        # Mock the LLM provider
        mock_llm_provider = Mock()
        mock_create_llm.return_value = mock_llm_provider

        docstringinator = Docstringinator()

        # Test docstring with triple quotes on separate lines
        docstring_with_quotes = '''"""
This is a test docstring.
"""
'''
        cleaned = docstringinator._clean_docstring(docstring_with_quotes)
        assert '"""' not in cleaned
        assert "This is a test docstring." in cleaned

        # Test docstring with triple quotes at start/end
        docstring_with_quotes_2 = '"""This is another test docstring."""'
        cleaned2 = docstringinator._clean_docstring(docstring_with_quotes_2)
        assert '"""' not in cleaned2
        assert "This is another test docstring." in cleaned2

        # Test docstring without triple quotes
        docstring_without_quotes = "This is a test docstring."
        cleaned3 = docstringinator._clean_docstring(docstring_without_quotes)
        assert cleaned3 == "This is a test docstring."

        # Test empty docstring
        empty_docstring = ""
        cleaned4 = docstringinator._clean_docstring(empty_docstring)
        assert cleaned4 == "No description available."

    @patch("docstringinator.core.create_llm_provider")
    @patch("docstringinator.core.load_config")
    @patch("docstringinator.core.validate_config")
    def test_end_to_end_multiple_functions(
        self, mock_validate_config, mock_load_config, mock_create_llm,
    ):
        """Test end-to-end docstring addition for multiple functions."""
        # Mock the configuration
        mock_config = Config(
            llm=LLMConfig(
                provider=LLMProvider.LOCAL,
                model="test-model",
                api_key="test-key",
                temperature=0.1,
            ),
        )
        mock_load_config.return_value = mock_config

        # Mock the LLM provider to return a simple docstring
        mock_llm_provider = Mock()
        mock_response = Mock()
        mock_response.content = "Test docstring."
        mock_llm_provider.generate_docstring.return_value = mock_response
        mock_create_llm.return_value = mock_llm_provider

        docstringinator = Docstringinator()

        # Create a test file with multiple functions
        test_content = """def simple_function():
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

        # Create temporary file
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_content)
            temp_file_path = f.name

        try:
            # Run docstringinator
            result = docstringinator.fix_file(temp_file_path)

            # Check that changes were made
            assert result.success
            assert len(result.changes) > 0

            # Read the result and check docstring placement
            with open(temp_file_path) as f:
                result_content = f.read()

            lines = result_content.split("\n")

            # Check that docstrings are placed correctly for each function
            # Simple function should have docstring after line 1
            simple_func_line = None
            for i, line in enumerate(lines):
                if line.strip() == "def simple_function():":
                    simple_func_line = i
                    break

            assert simple_func_line is not None
            # Docstring should be on the line after the function definition
            # The docstring is inserted as multiple lines: opening quote, content, closing quote
            # Since the function definition is at simple_func_line, the docstring should be at simple_func_line + 1
            docstring_start_line = simple_func_line + 1
            assert docstring_start_line < len(lines)
            assert '"""' in lines[docstring_start_line]

            # Return statement should come after the docstring
            return_line = None
            for i in range(
                docstring_start_line + 2, len(lines),
            ):  # Skip the docstring lines (new format: opening+content line, closing line)
                if "return True" in lines[i]:
                    return_line = i
                    break

            assert return_line is not None
            assert return_line > docstring_start_line

        finally:
            # Clean up
            os.unlink(temp_file_path)

    @patch("docstringinator.core.create_llm_provider")
    @patch("docstringinator.core.load_config")
    @patch("docstringinator.core.validate_config")
    def test_docstring_placement_accuracy(
        self, mock_validate_config, mock_load_config, mock_create_llm,
    ):
        """Test that docstrings are placed in the correct positions."""
        # Mock the configuration
        mock_config = Config(
            llm=LLMConfig(
                provider=LLMProvider.LOCAL,
                model="test-model",
                api_key="test-key",
                temperature=0.1,
            ),
        )
        mock_load_config.return_value = mock_config

        # Mock the LLM provider to return a simple docstring
        mock_llm_provider = Mock()
        mock_response = Mock()
        mock_response.content = "Test docstring."
        mock_llm_provider.generate_docstring.return_value = mock_response
        mock_create_llm.return_value = mock_llm_provider

        docstringinator = Docstringinator()

        # Create a test file with specific structure
        test_content = """def function1():
    return True

def function2(
    param1: str,
    param2: int
) -> dict:
    return {"param1": param1, "param2": param2}

def function3():
    return False
"""

        # Create temporary file
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_content)
            temp_file_path = f.name

        try:
            # Run docstringinator
            result = docstringinator.fix_file(temp_file_path)

            # Check that changes were made
            assert result.success
            assert len(result.changes) > 0

            # Read the result and check docstring placement
            with open(temp_file_path) as f:
                result_content = f.read()

            lines = result_content.split("\n")

            # Find function positions
            func1_line = None
            func2_line = None
            func3_line = None

            for i, line in enumerate(lines):
                if line.strip() == "def function1():":
                    func1_line = i
                elif line.strip() == "def function2(":
                    func2_line = i
                elif line.strip() == "def function3():":
                    func3_line = i

            # Check that all functions were found
            assert func1_line is not None
            assert func2_line is not None
            assert func3_line is not None

            # Check that docstrings are placed after function definitions, not after return statements
            # Function 1 docstring should be after function definition
            if func1_line + 1 < len(lines):
                assert '"""' in lines[func1_line + 1]

                # Function 2 docstring should be after function signature (not in the middle)
                # Find where function 2 signature ends (after the closing parenthesis)
                func2_signature_end = None
                for i in range(func2_line, len(lines)):
                    if "-> dict:" in lines[i]:
                        func2_signature_end = i
                        break

                if func2_signature_end is not None:
                    # Docstring should be right after the signature
                    assert '"""' in lines[func2_signature_end + 1]

        finally:
            # Clean up
            os.unlink(temp_file_path)
