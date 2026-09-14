"""AST and structural code parser for Python and multi-language repositories."""

import ast
from dataclasses import dataclass, field
import re
from typing import List, Optional, Set


@dataclass
class ParsedSymbol:
    """Represents a code symbol (function, class, method, etc.) extracted from AST."""

    name: str
    symbol_type: str  # function, async_function, class, method, async_method, module
    start_line: int
    end_line: int
    parent_name: Optional[str] = None
    docstring: Optional[str] = None
    code_text: str = ""
    is_async: bool = False
    imports: List[str] = field(default_factory=list)
    calls: List[str] = field(default_factory=list)


class CodeParser:
    """Parses source code files into structural symbol representations."""

    @classmethod
    def parse_file(cls, content: str, language: str) -> List[ParsedSymbol]:
        """Parse source code content based on language."""

        if language == "python":
            symbols = cls._parse_python(content)
            if symbols:
                return symbols

        # Fallback to regex structural parser for JS/TS/Java/Go/C++ or unparsed python
        return cls._parse_generic_structural(content, language)

    @classmethod
    def _parse_python(cls, content: str) -> List[ParsedSymbol]:
        """Parse Python source code using standard library `ast`."""
        symbols: List[ParsedSymbol] = []
        lines = content.splitlines()

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return []

        # Extract top-level imports
        file_imports: List[str] = []
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    file_imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    file_imports.append(f"{module}.{alias.name}" if module else alias.name)

        # Visitor for classes and functions
        class SymbolVisitor(ast.NodeVisitor):
            def __init__(self):
                self.current_parent: Optional[str] = None

            def visit_ClassDef(self, node: ast.ClassDef):
                docstring = ast.get_docstring(node)
                start = node.lineno
                end = getattr(node, "end_lineno", start)
                code_text = "\n".join(lines[start - 1 : end])

                symbols.append(
                    ParsedSymbol(
                        name=node.name,
                        symbol_type="class",
                        start_line=start,
                        end_line=end,
                        parent_name=self.current_parent,
                        docstring=docstring,
                        code_text=code_text,
                        imports=file_imports.copy(),
                        calls=cls._extract_calls_from_ast(node),
                    )
                )

                previous_parent = self.current_parent
                self.current_parent = node.name
                self.generic_visit(node)
                self.current_parent = previous_parent

            def visit_FunctionDef(self, node: ast.FunctionDef):
                self._handle_function(node, is_async=False)

            def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
                self._handle_function(node, is_async=True)

            def _handle_function(self, node, is_async: bool):
                docstring = ast.get_docstring(node)
                start = node.lineno
                end = getattr(node, "end_lineno", start)
                code_text = "\n".join(lines[start - 1 : end])

                if self.current_parent:
                    sym_type = "async_method" if is_async else "method"
                else:
                    sym_type = "async_function" if is_async else "function"

                symbols.append(
                    ParsedSymbol(
                        name=node.name,
                        symbol_type=sym_type,
                        start_line=start,
                        end_line=end,
                        parent_name=self.current_parent,
                        docstring=docstring,
                        code_text=code_text,
                        is_async=is_async,
                        imports=file_imports.copy(),
                        calls=cls._extract_calls_from_ast(node),
                    )
                )
                self.generic_visit(node)

        visitor = SymbolVisitor()
        visitor.visit(tree)
        return symbols

    @staticmethod
    def _extract_calls_from_ast(node: ast.AST) -> List[str]:
        """Extract called function/method names within an AST node."""
        calls: Set[str] = set()
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.add(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    calls.add(child.func.attr)
        return list(calls)

    @classmethod
    def _parse_generic_structural(cls, content: str, language: str) -> List[ParsedSymbol]:
        """Regex structural block parser fallback for generic code files."""
        symbols: List[ParsedSymbol] = []
        lines = content.splitlines()
        if not lines:
            return symbols

        # Patterns for common languages (JS, TS, Java, C++, Go)
        func_patterns = [
            r"function\s+([A-Za-z0-9_]+)\s*\(",
            r"(?:const|let|var)\s+([A-Za-z0-9_]+)\s*=\s*(?:async\s*)?\(",
            r"(?:public|private|protected|static|\s)*\s+([A-Za-z0-9_]+)\s*\([^)]*\)\s*\{",
            r"func\s+(?:\([^)]+\)\s*)?([A-Za-z0-9_]+)\s*\(",
            r"def\s+([A-Za-z0-9_]+)\s*\(",
        ]

        class_patterns = [
            r"class\s+([A-Za-z0-9_]+)",
            r"interface\s+([A-Za-z0-9_]+)",
            r"struct\s+([A-Za-z0-9_]+)",
        ]

        for i, line in enumerate(lines, 1):
            # Match functions
            for pat in func_patterns:
                m = re.search(pat, line)
                if m:
                    sym_name = m.group(1)
                    start = i
                    end = min(i + 30, len(lines))
                    code_text = "\n".join(lines[start - 1 : end])
                    symbols.append(
                        ParsedSymbol(
                            name=sym_name,
                            symbol_type="function",
                            start_line=start,
                            end_line=end,
                            code_text=code_text,
                        )
                    )
                    break

            # Match classes
            for pat in class_patterns:
                m = re.search(pat, line)
                if m:
                    sym_name = m.group(1)
                    start = i
                    end = min(i + 50, len(lines))
                    code_text = "\n".join(lines[start - 1 : end])
                    symbols.append(
                        ParsedSymbol(
                            name=sym_name,
                            symbol_type="class",
                            start_line=start,
                            end_line=end,
                            code_text=code_text,
                        )
                    )
                    break

        return symbols
