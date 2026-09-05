"""Tree-sitter Python parsing integration."""

from pathlib import Path
from typing import Optional

import tree_sitter
import tree_sitter_python
from tree_sitter import Language, Node, Parser

from backend.app.models.analyzer import ClassInfo, FunctionInfo, ImportInfo, MethodInfo, PythonFileAnalysis
from backend.app.services.analyzer.config import MAX_FILE_SIZE
from backend.app.services.analyzer.discovery import is_binary

# Initialize the Python language for tree-sitter
PY_LANGUAGE = Language(tree_sitter_python.language())

def analyze_python_file(file_path: Path, relative_posix_path: str) -> PythonFileAnalysis:
    """Analyze a single Python file using tree-sitter.

    Returns a structured PythonFileAnalysis indicating success or parsing error.
    Handles size limits and binary accidental executions.
    """
    if not file_path.exists() or not file_path.is_file():
        return PythonFileAnalysis(success=False, file_path=relative_posix_path, error="File does not exist")
        
    try:
        if file_path.stat().st_size > MAX_FILE_SIZE:
            return PythonFileAnalysis(success=False, file_path=relative_posix_path, error="File size exceeds limit")
            
        if is_binary(file_path):
            return PythonFileAnalysis(success=False, file_path=relative_posix_path, error="File is binary")
            
        content_bytes = file_path.read_bytes()
    except OSError as e:
        return PythonFileAnalysis(success=False, file_path=relative_posix_path, error=f"Read error: {str(e)}")

    parser = Parser(PY_LANGUAGE)
    tree = parser.parse(content_bytes)

    # A simplistic error check: if the root node has ERROR children, it's malformed.
    # While tree-sitter handles errors gracefully, we will flag it if the root has syntax errors.
    if tree.root_node.has_error:
        return PythonFileAnalysis(
            success=False,
            file_path=relative_posix_path,
            error="Unable to parse Python source"
        )
        
    classes = []
    functions = []
    imports = []
    
    # Traverse tree
    for child in tree.root_node.children:
        if child.type == "class_definition":
            cls_info = _parse_class(child, content_bytes)
            if cls_info:
                classes.append(cls_info)
        elif child.type == "function_definition":
            func_info = _parse_function(child, content_bytes)
            if func_info:
                functions.append(func_info)
        elif child.type == "import_statement":
            imports.extend(_parse_import(child, content_bytes))
        elif child.type == "import_from_statement":
            imports.extend(_parse_import_from(child, content_bytes))
            
    return PythonFileAnalysis(
        success=True,
        file_path=relative_posix_path,
        classes=classes,
        functions=functions,
        imports=imports
    )


def _get_text(node: Optional[Node], code: bytes) -> str:
    """Extract text from a given node safely."""
    if not node:
        return ""
    return code[node.start_byte:node.end_byte].decode("utf-8", errors="ignore")


def _parse_function(node: Node, code: bytes) -> Optional[FunctionInfo]:
    """Parse a function_definition node."""
    name_node = node.child_by_field_name("name")
    if not name_node:
        return None
        
    name = _get_text(name_node, code)
    args = []
    
    params_node = node.child_by_field_name("parameters")
    if params_node:
        # tree-sitter parameters list has children like identifiers or typed_parameters
        for child in params_node.children:
            if child.type in ("identifier", "typed_parameter", "default_parameter", "list_splat_pattern", "dictionary_splat_pattern"):
                # Simplify: just get the full text of the parameter (e.g. self, x: int, *args)
                args.append(_get_text(child, code))
                
    return FunctionInfo(
        name=name,
        args=args,
        start_line=node.start_point[0] + 1,
        end_line=node.end_point[0] + 1
    )


def _parse_class(node: Node, code: bytes) -> Optional[ClassInfo]:
    """Parse a class_definition node."""
    name_node = node.child_by_field_name("name")
    if not name_node:
        return None
        
    name = _get_text(name_node, code)
    methods = []
    
    body = node.child_by_field_name("body")
    if body:
        for child in body.children:
            if child.type == "function_definition":
                f_info = _parse_function(child, code)
                if f_info:
                    methods.append(MethodInfo(
                        name=f_info.name,
                        args=f_info.args,
                        start_line=f_info.start_line,
                        end_line=f_info.end_line
                    ))
                    
    return ClassInfo(
        name=name,
        methods=methods,
        start_line=node.start_point[0] + 1,
        end_line=node.end_point[0] + 1
    )


def _parse_import(node: Node, code: bytes) -> list[ImportInfo]:
    """Parse an import_statement node. Example: import a, b.c"""
    results = []
    # Contains aliased_import or dotted_name children
    for child in node.children:
        if child.type in ("dotted_name", "aliased_import"):
            module = _get_text(child, code)
            results.append(ImportInfo(
                module=module,
                names=[],
                line_number=node.start_point[0] + 1
            ))
    return results


def _parse_import_from(node: Node, code: bytes) -> list[ImportInfo]:
    """Parse an import_from_statement node. Example: from a import b, c"""
    module_node = node.child_by_field_name("module_name")
    
    # If module_name is None, it might be a relative import like `from . import b`
    module = _get_text(module_node, code) if module_node else "."
    
    names = []
    for child in node.children:
        # tree-sitter gives names as dotted_name or aliased_import within the import list
        if child.type == "dotted_name" and child != module_node:
            names.append(_get_text(child, code))
        elif child.type == "aliased_import":
            names.append(_get_text(child, code))
            
    return [ImportInfo(
        module=module,
        names=names,
        line_number=node.start_point[0] + 1
    )]
