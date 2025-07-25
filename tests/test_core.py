"""Tests for the core Docstringinator functionality."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from docstringinator.core import Docstringinator
from docstringinator.models import ProcessingResult, BatchResult, Config, LLMConfig, LLMProvider


class TestDocstringinator:
    """Test the main Docstringinator class."""

    @patch('docstringinator.core.create_llm_provider')
    @patch('docstringinator.core.load_config')
    @patch('docstringinator.core.validate_config')
    def test_initialisation(self, mock_validate_config, mock_load_config, mock_create_llm):
        """Test that Docstringinator can be initialised."""
        # Mock the configuration
        mock_config = Config(
            llm=LLMConfig(
                provider=LLMProvider.LOCAL,
                model="test-model",
                api_key="test-key",
                temperature=0.1
            )
        )
        mock_load_config.return_value = mock_config
        
        # Mock the LLM provider
        mock_llm_provider = Mock()
        mock_create_llm.return_value = mock_llm_provider
        
        docstringinator = Docstringinator()
        assert docstringinator is not None
        assert hasattr(docstringinator, 'config')
        assert hasattr(docstringinator, 'llm_provider')
        assert hasattr(docstringinator, 'extractor')

    @patch('docstringinator.core.create_llm_provider')
    @patch('docstringinator.core.load_config')
    @patch('docstringinator.core.validate_config')
    def test_fix_file_with_invalid_path(self, mock_validate_config, mock_load_config, mock_create_llm):
        """Test that invalid file paths raise appropriate errors."""
        # Mock the configuration
        mock_config = Config(
            llm=LLMConfig(
                provider=LLMProvider.LOCAL,
                model="test-model",
                api_key="test-key",
                temperature=0.1
            )
        )
        mock_load_config.return_value = mock_config
        
        # Mock the LLM provider
        mock_llm_provider = Mock()
        mock_create_llm.return_value = mock_llm_provider
        
        docstringinator = Docstringinator()
        
        with pytest.raises(FileNotFoundError):
            docstringinator.fix_file("nonexistent_file.py")

    @patch('docstringinator.core.create_llm_provider')
    @patch('docstringinator.core.load_config')
    @patch('docstringinator.core.validate_config')
    def test_fix_file_with_non_python_file(self, mock_validate_config, mock_load_config, mock_create_llm):
        """Test that non-Python files raise appropriate errors."""
        # Mock the configuration
        mock_config = Config(
            llm=LLMConfig(
                provider=LLMProvider.LOCAL,
                model="test-model",
                api_key="test-key",
                temperature=0.1
            )
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
            with pytest.raises(ValueError, match="File must be a Python file"):
                docstringinator.fix_file(str(temp_file))
        finally:
            temp_file.unlink(missing_ok=True)

    @patch('docstringinator.core.create_llm_provider')
    @patch('docstringinator.core.load_config')
    @patch('docstringinator.core.validate_config')
    def test_fix_directory_with_invalid_path(self, mock_validate_config, mock_load_config, mock_create_llm):
        """Test that invalid directory paths raise appropriate errors."""
        # Mock the configuration
        mock_config = Config(
            llm=LLMConfig(
                provider=LLMProvider.LOCAL,
                model="test-model",
                api_key="test-key",
                temperature=0.1
            )
        )
        mock_load_config.return_value = mock_config
        
        # Mock the LLM provider
        mock_llm_provider = Mock()
        mock_create_llm.return_value = mock_llm_provider
        
        docstringinator = Docstringinator()
        
        with pytest.raises(FileNotFoundError):
            docstringinator.fix_directory("nonexistent_directory")

    @patch('docstringinator.core.create_llm_provider')
    @patch('docstringinator.core.load_config')
    @patch('docstringinator.core.validate_config')
    def test_fix_directory_with_file_path(self, mock_validate_config, mock_load_config, mock_create_llm):
        """Test that file paths passed to fix_directory raise appropriate errors."""
        # Mock the configuration
        mock_config = Config(
            llm=LLMConfig(
                provider=LLMProvider.LOCAL,
                model="test-model",
                api_key="test-key",
                temperature=0.1
            )
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
            with pytest.raises(ValueError, match="Path must be a directory"):
                docstringinator.fix_directory(str(temp_file))
        finally:
            temp_file.unlink(missing_ok=True)

    @patch('docstringinator.core.Docstringinator._process_file')
    @patch('docstringinator.core.create_llm_provider')
    @patch('docstringinator.core.load_config')
    @patch('docstringinator.core.validate_config')
    def test_fix_file_success(self, mock_validate_config, mock_load_config, mock_create_llm, mock_process_file):
        """Test successful file processing."""
        # Mock the configuration
        mock_config = Config(
            llm=LLMConfig(
                provider=LLMProvider.LOCAL,
                model="test-model",
                api_key="test-key",
                temperature=0.1
            )
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

    @patch('docstringinator.core.Docstringinator._process_directory')
    @patch('docstringinator.core.create_llm_provider')
    @patch('docstringinator.core.load_config')
    @patch('docstringinator.core.validate_config')
    def test_fix_directory_success(self, mock_validate_config, mock_load_config, mock_create_llm, mock_process_directory):
        """Test successful directory processing."""
        # Mock the configuration
        mock_config = Config(
            llm=LLMConfig(
                provider=LLMProvider.LOCAL,
                model="test-model",
                api_key="test-key",
                temperature=0.1
            )
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

    @patch('docstringinator.core.create_llm_provider')
    @patch('docstringinator.core.load_config')
    @patch('docstringinator.core.validate_config')
    def test_preview_changes(self, mock_validate_config, mock_load_config, mock_create_llm):
        """Test preview_changes method."""
        # Mock the configuration
        mock_config = Config(
            llm=LLMConfig(
                provider=LLMProvider.LOCAL,
                model="test-model",
                api_key="test-key",
                temperature=0.1
            )
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
            changes = docstringinator.preview_changes(str(temp_file))
            assert isinstance(changes, list)
        finally:
            temp_file.unlink(missing_ok=True)

    @patch('docstringinator.core.create_llm_provider')
    @patch('docstringinator.core.load_config')
    @patch('docstringinator.core.validate_config')
    def test_fix_string(self, mock_validate_config, mock_load_config, mock_create_llm):
        """Test fix_string method."""
        # Mock the configuration
        mock_config = Config(
            llm=LLMConfig(
                provider=LLMProvider.LOCAL,
                model="test-model",
                api_key="test-key",
                temperature=0.1
            )
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

    @patch('docstringinator.core.create_llm_provider')
    @patch('docstringinator.core.load_config')
    @patch('docstringinator.core.validate_config')
    def test_should_improve_docstring(self, mock_validate_config, mock_load_config, mock_create_llm):
        """Test _should_improve_docstring method."""
        # Mock the configuration
        mock_config = Config(
            llm=LLMConfig(
                provider=LLMProvider.LOCAL,
                model="test-model",
                api_key="test-key",
                temperature=0.1
            )
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

    @patch('docstringinator.core.create_llm_provider')
    @patch('docstringinator.core.load_config')
    @patch('docstringinator.core.validate_config')
    def test_print_results(self, mock_validate_config, mock_load_config, mock_create_llm):
        """Test print_results method."""
        # Mock the configuration
        mock_config = Config(
            llm=LLMConfig(
                provider=LLMProvider.LOCAL,
                model="test-model",
                api_key="test-key",
                temperature=0.1
            )
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

    @patch('docstringinator.core.create_llm_provider')
    @patch('docstringinator.core.load_config')
    @patch('docstringinator.core.validate_config')
    def test_print_batch_results(self, mock_validate_config, mock_load_config, mock_create_llm):
        """Test print_batch_results method."""
        # Mock the configuration
        mock_config = Config(
            llm=LLMConfig(
                provider=LLMProvider.LOCAL,
                model="test-model",
                api_key="test-key",
                temperature=0.1
            )
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