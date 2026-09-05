"""Tests for tree-sitter Python parser."""

from pathlib import Path

from backend.app.services.analyzer.parser import analyze_python_file

FIXTURE_PATH = Path("backend/tests/fixtures/fixture_project").resolve()

def test_analyze_valid_python_file():
    """Functions, classes, imports, and methods are extracted correctly."""
    file_path = FIXTURE_PATH / "app" / "main.py"
    
    analysis = analyze_python_file(file_path, "app/main.py")
    assert analysis.success is True
    assert analysis.file_path == "app/main.py"
    
    # Check imports
    imported_modules = [imp.module for imp in analysis.imports]
    assert "os" in imported_modules
    assert "." in imported_modules  # relative import
    
    # Check standalone functions
    funcs = [f.name for f in analysis.functions]
    assert "standalone_function" in funcs
    
    target_func = next(f for f in analysis.functions if f.name == "standalone_function")
    assert "x" in target_func.args or "x: int" in target_func.args
    assert "y" in target_func.args or "y: int" in target_func.args
    
    # Check classes
    classes = [c.name for c in analysis.classes]
    assert "UserService" in classes
    
    target_cls = next(c for c in analysis.classes if c.name == "UserService")
    
    # Check methods
    methods = [m.name for m in target_cls.methods]
    assert "__init__" in methods
    assert "get_user" in methods
    assert "_private_method" in methods

def test_analyze_malformed_python_file():
    """Malformed python files fail parsing successfully without crashing."""
    file_path = FIXTURE_PATH / "app" / "broken.py"
    
    analysis = analyze_python_file(file_path, "app/broken.py")
    assert analysis.success is False
    assert analysis.error == "Unable to parse Python source"

def test_analyze_large_file():
    """Extremely large files are skipped."""
    file_path = FIXTURE_PATH / "huge.txt"
    analysis = analyze_python_file(file_path, "huge.txt")
    assert analysis.success is False
    assert analysis.error == "File size exceeds limit"

def test_analyze_binary_file():
    """Binary files are rejected gracefully."""
    file_path = FIXTURE_PATH / "image.png"
    analysis = analyze_python_file(file_path, "image.png")
    assert analysis.success is False
    assert analysis.error == "File is binary"
