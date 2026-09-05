"""Tests for regex-based and python-based code searching."""

from pathlib import Path

from backend.app.services.analyzer.search import search_code, _python_fallback_search

FIXTURE_PATH = Path("backend/tests/fixtures/fixture_project").resolve()

def test_search_code_finds_term():
    """Standard search locates term."""
    results = search_code(str(FIXTURE_PATH), "UNIQUE_SEARCH_TERM")
    assert len(results) >= 1
    
    # At least one result should be in main.py
    main_results = [r for r in results if r.file_path == "app/main.py"]
    assert len(main_results) == 1
    
    res = main_results[0]
    assert "UNIQUE_SEARCH_TERM" in res.matching_line
    assert res.line_number > 0

def test_search_code_not_found():
    """Searching a nonexistent term yields empty list."""
    results = search_code(str(FIXTURE_PATH), "THIS_WILL_NEVER_EXIST_99999")
    assert len(results) == 0

def test_python_fallback_search():
    """Fallback search explicitly tested to ensure parity if rg missing."""
    results = _python_fallback_search(FIXTURE_PATH, "UNIQUE_SEARCH_TERM")
    assert len(results) == 1
    
    res = results[0]
    assert res.file_path == "app/main.py"
    assert "UNIQUE_SEARCH_TERM" in res.matching_line
    assert res.line_number > 0
    
def test_fallback_search_ignores_huge():
    """Make sure fallback ignores big/bin files so it doesn't crash."""
    results = _python_fallback_search(FIXTURE_PATH, "0000000") # huge.txt has exactly this
    # It should yield 0 results because huge.txt is skipped due to size.
    assert len(results) == 0
