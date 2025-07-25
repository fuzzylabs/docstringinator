"""Python code parser for extracting function information."""

import ast
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .exceptions import ParseError
from .models import DocstringInfo


class PythonParser:
    """Parser for Python code to extract function information."""

    def __init__(self) -> None:
        """Initialise the parser."""
        self.module_name = ""

    def parse_file(self, file_path: str) -> List[DocstringInfo]:
        """Parse a Python file and extract function information.

        Args:
            file_path: Path to the Python file.

        Returns:
            List of function information objects.
        """
        try:
            with Path(file_path).open(encoding="utf-8") as f:
                content = f.read()

            self.module_name = Path(file_path).stem
            tree = ast.parse(content)
            self._build_parent_relationships(tree)
            return self._extract_functions(tree, content)

        except Exception as e:
            raise ParseError from e

    def parse_string(
        self,
        code: str,
    ) -> List[DocstringInfo]:
        """Parse Python code string and extract function information.

        Args:
            code: Python code as string.

        Returns:
            List of function information objects.
        """
        try:
            tree = ast.parse(code)
            self._build_parent_relationships(tree)
            return self._extract_functions(tree, code)

        except Exception as e:
            raise ParseError from e

    def _extract_functions(
        self,
        tree: ast.AST,
        source_code: str,
    ) -> List[DocstringInfo]:
        """Extract function information from AST.

        Args:
            tree: Parsed AST.
            source_code: Original source code.

        Returns:
            List of function information objects.
        """
        functions = []
        lines = source_code.split("\n")

        # Build parent-child relationships
        self._build_parent_relationships(tree)

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_info = self._extract_function_info(node, lines)
                if func_info:
                    functions.append(func_info)

        return functions

    def _build_parent_relationships(
        self,
        node: ast.AST,
        parent: Optional[ast.AST] = None,
    ) -> None:
        """Build parent-child relationships in the AST.

        Args:
            node: Current AST node.
            parent: Parent AST node.
        """
        node.parent = parent  # type: ignore[attr-defined]

        for child in ast.iter_child_nodes(node):
            self._build_parent_relationships(child, node)

    def _extract_function_info(
        self,
        node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
        lines: List[str],
    ) -> Optional[DocstringInfo]:
        """Extract information about a single function.

        Args:
            node: Function definition AST node.
            lines: Source code lines.

        Returns:
            Function information object or None if function should be skipped.
        """
        # Skip private functions and test functions
        if node.name.startswith("_") and not node.name.startswith("__"):
            return None

        if node.name.startswith("test_"):
            return None

        # Get class name if this is a method
        class_name = self._get_class_name(node)

        # Extract signature
        signature = self._get_function_signature(node, lines)

        # Extract parameters
        parameters = self._extract_parameters(node)

        # Extract return type
        return_type = self._get_return_type(node)

        # Check for existing docstring
        existing_docstring = self._extract_existing_docstring(node)

        # Get line numbers
        line_number = node.lineno
        end_line_number = self._get_function_end_line(node, lines)

        # For docstring insertion, we need the line after the function signature ends
        # Find where the function signature actually ends (where the colon is)
        signature_end_line = self._get_function_signature_end_line(node, lines)

        # Extract function body for context (first few lines)
        function_body = self._extract_function_body(node, lines)

        return DocstringInfo(
            function_name=node.name,
            class_name=class_name,
            module_name=self.module_name,
            signature=signature,
            existing_docstring=existing_docstring,
            line_number=signature_end_line,  # Use signature end line for docstring insertion
            end_line_number=end_line_number,
            has_docstring=existing_docstring is not None,
            is_method=class_name is not None,
            is_async=isinstance(node, ast.AsyncFunctionDef),
            return_type=return_type,
            parameters=parameters,
            function_body=function_body,
        )

    def _get_class_name(
        self,
        node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
    ) -> Optional[str]:
        """Get the name of the class if this function is a method.

        Args:
            node: Function definition AST node.

        Returns:
            Class name or None if not a method.
        """
        parent = getattr(node, "parent", None)
        while parent is not None:
            if isinstance(parent, ast.ClassDef):
                return parent.name
            parent = getattr(parent, "parent", None)
        return None

    def _get_function_signature(
        self,
        node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
        lines: List[str],
    ) -> str:
        """Extract the function signature as a string.

        Args:
            node: Function definition AST node.
            lines: Source code lines.

        Returns:
            Function signature string.
        """
        # Reconstruct the signature from the AST for better accuracy
        signature_parts = []

        # Add async keyword if present
        if isinstance(node, ast.AsyncFunctionDef):
            signature_parts.append("async")

        # Add function name
        signature_parts.append(f"def {node.name}")

        # Add parameters
        args = []
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            args.append(arg_str)

        # Add defaults
        defaults = node.args.defaults
        required_count = len(args) - len(defaults)

        for i, arg in enumerate(args):
            if i >= required_count:
                default_index = i - required_count
                if default_index < len(defaults):
                    default_value = ast.unparse(defaults[default_index])
                    args[i] += f" = {default_value}"

        # Add *args if present
        if node.args.vararg:
            vararg_str = f"*{node.args.vararg.arg}"
            if node.args.vararg.annotation:
                vararg_str += f": {ast.unparse(node.args.vararg.annotation)}"
            args.append(vararg_str)

        # Add **kwargs if present
        if node.args.kwarg:
            kwarg_str = f"**{node.args.kwarg.arg}"
            if node.args.kwarg.annotation:
                kwarg_str += f": {ast.unparse(node.args.kwarg.annotation)}"
            args.append(kwarg_str)

        signature_parts.append(f"({', '.join(args)})")

        # Add return type if present
        if node.returns:
            signature_parts.append(f" -> {ast.unparse(node.returns)}")

        return " ".join(signature_parts)

    def _extract_parameters(
        self,
        node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
    ) -> List[Dict[str, Any]]:
        """Extract function parameters.

        Args:
            node: Function definition AST node.

        Returns:
            List of parameter dictionaries.
        """
        parameters = []

        for arg in node.args.args:
            param_info = {
                "name": arg.arg,
                "type": self._get_parameter_type(arg),
                "default": None,
                "required": True,
            }

            # Check if parameter has a default value
            param_index = node.args.args.index(arg)
            if param_index >= len(node.args.args) - len(node.args.defaults):
                default_index = param_index - (
                    len(node.args.args) - len(node.args.defaults)
                )
                if default_index >= 0:
                    param_info["default"] = self._get_default_value(
                        node.args.defaults[default_index],
                    )
                    param_info["required"] = False

            parameters.append(param_info)

        # Handle *args
        if node.args.vararg:
            parameters.append(
                {
                    "name": node.args.vararg.arg,
                    "type": "Any",
                    "default": None,
                    "required": False,
                    "vararg": True,
                },
            )

        # Handle **kwargs
        if node.args.kwarg:
            parameters.append(
                {
                    "name": node.args.kwarg.arg,
                    "type": "Any",
                    "default": None,
                    "required": False,
                    "kwarg": True,
                },
            )

        return parameters

    def _get_parameter_type(self, arg: ast.arg) -> str:
        """Get the type annotation for a parameter.

        Args:
            arg: Parameter AST node.

        Returns:
            Type annotation string.
        """
        if arg.annotation is None:
            return "Any"

        return ast.unparse(arg.annotation)

    def _get_default_value(self, default: ast.expr) -> str:
        """Get the default value for a parameter.

        Args:
            default: Default value AST node.

        Returns:
            Default value string.
        """
        return ast.unparse(default)

    def _get_return_type(
        self,
        node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
    ) -> Optional[str]:
        """Get the return type annotation.

        Args:
            node: Function definition AST node.

        Returns:
            Return type string or None.
        """
        if node.returns is None:
            return None

        return ast.unparse(node.returns)

    def _extract_existing_docstring(
        self,
        node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
    ) -> Optional[str]:
        """Extract existing docstring from function."""
        if node.body:
            first_stmt = node.body[0]
            if (
                isinstance(first_stmt, ast.Expr)
                and isinstance(first_stmt.value, ast.Constant)
                and isinstance(first_stmt.value.value, str)
            ):
                return first_stmt.value.value
        return None

    def _get_function_end_line(
        self,
        node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
        lines: List[str],
    ) -> int:
        """Get the end line number of the function.

        Args:
            node: Function definition AST node.
            lines: Source code lines.

        Returns:
            End line number.
        """
        # Simple heuristic: find the next function or class definition
        start_line = node.lineno

        for i, line in enumerate(lines[start_line:], start_line + 1):
            stripped = line.strip()
            if stripped.startswith(("def ", "class ")):
                return i - 1

        return len(lines)

    def _get_function_signature_end_line(
        self,
        node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
        lines: List[str],
    ) -> int:
        """
        Get the line number where the function signature ends (where the colon is).
        """
        start_line = node.lineno - 1  # Convert to 0-based index

        # Walk forward from the start line until we find a line that ends the signature
        for i in range(start_line, len(lines)):
            line = lines[i]
            line_stripped = line.strip()

            # Skip empty lines and comments
            if not line_stripped or line_stripped.startswith("#"):
                continue

            # Look for a line that ends with a colon - this indicates the end of a function signature
            # This check must come BEFORE checking for function body elements
            # Handle cases where the colon is followed by a comment
            if line_stripped.endswith(":"):
                return i + 1  # 1-based index for insertion
            if ":" in line_stripped:
                # Check if the colon is followed by a comment
                colon_index = line_stripped.find(":")
                if colon_index != -1:
                    # Check if everything after the colon is just a comment
                    after_colon = line_stripped[colon_index + 1 :].strip()
                    if not after_colon or after_colon.startswith("#"):
                        return i + 1  # 1-based index for insertion

            # If we find a line that's not indented and looks like a new function/class, we've gone too far
            if i > start_line and line_stripped and not line.startswith((" ", "\t")):
                if line_stripped.startswith(("def ", "class ", "@")):
                    break

            # If we find a docstring, function body, or another function/class, we've gone too far
            if (
                line_stripped.startswith('"""')
                or line_stripped.startswith("'''")
                or line_stripped.startswith("return ")
                or line_stripped.startswith("pass")
            ):
                break

        # Fallback: return the start line + 1
        return start_line + 1

    def _extract_function_body(
        self,
        node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
        lines: List[str],
    ) -> Optional[str]:
        """Extract the function body as a string.

        Args:
            node: Function definition AST node.
            lines: Source code lines.

        Returns:
            Function body string or None if no body.
        """
        try:
            # Find where the function signature ends (where the colon is)
            signature_end_line = self._get_function_signature_end_line(node, lines)
            function_end_line = self._get_function_end_line(node, lines)

            # Convert to 0-based indexing for array access
            start_idx = signature_end_line  # signature_end_line is already 1-based, so this gives us the line after the colon
            end_idx = min(
                start_idx + 10, function_end_line, len(lines),
            )  # Limit to first 10 lines or function end

            if start_idx >= len(lines) or start_idx >= end_idx:
                return None

            # Extract the body lines
            body_lines = []
            for i in range(start_idx, end_idx):
                if i < len(lines):
                    line = lines[i].rstrip()
                    # Skip empty lines at the beginning
                    if not body_lines and not line.strip():
                        continue
                    # Stop if we hit another function or class definition
                    if line.strip().startswith(
                        ("def ", "class ", "@"),
                    ) and not line.strip().startswith("    "):
                        break
                    body_lines.append(line)

            if not body_lines:
                return None

            # Join the lines and limit length for context
            body = "\n".join(body_lines)

            # Truncate if too long (keep it reasonable for the prompt)
            if len(body) > 500:
                body = body[:500] + "\n    # ... (truncated)"

            return body

        except Exception:
            # If anything goes wrong, return None
            return None


class DocstringExtractor:
    """Extract and manipulate docstrings in Python code."""

    def __init__(self) -> None:
        """Initialise the extractor."""
        self.parser = PythonParser()

    def extract_docstrings(self, file_path: Path) -> List[DocstringInfo]:
        """Extract docstring information from a Python file.

        Args:
            file_path: Path to the Python file.

        Returns:
            List of docstring information objects.
        """
        return self.parser.parse_file(str(file_path))

    def find_missing_docstrings(self, file_path: Path) -> List[DocstringInfo]:
        """Find functions that are missing docstrings.

        Args:
            file_path: Path to the Python file.

        Returns:
            List of functions without docstrings.
        """
        functions = self.extract_docstrings(file_path)
        return [func for func in functions if not func.has_docstring]

    def find_poor_docstrings(self, file_path: Path) -> List[DocstringInfo]:
        """Find functions with poor or incomplete docstrings.

        Args:
            file_path: Path to the Python file.

        Returns:
            List of functions with poor docstrings.
        """
        functions = self.extract_docstrings(file_path)
        poor_docstrings = []

        for func in functions:
            if func.has_docstring and func.existing_docstring:
                # Check if docstring is too short or lacks key elements
                docstring = func.existing_docstring.strip()
                if len(docstring) < 20:  # Very short docstring
                    poor_docstrings.append(func)
                elif not any(
                    keyword in docstring.lower()
                    for keyword in ["param", "arg", "return", "raises"]
                ):
                    # Missing key documentation elements
                    poor_docstrings.append(func)

        return poor_docstrings

    def get_function_code(self, file_path: Path, function_name: str) -> Optional[str]:
        """Get the source code for a specific function.

        Args:
            file_path: Path to the Python file.
            function_name: Name of the function.

        Returns:
            Function source code or None if not found.
        """
        functions = self.extract_docstrings(file_path)

        for func in functions:
            if func.function_name == function_name:
                with Path(file_path).open(encoding="utf-8") as f:
                    lines = f.readlines()

                # Extract the function code
                start_line = func.line_number - 1
                end_line = func.end_line_number
                return "".join(lines[start_line:end_line])

        return None
