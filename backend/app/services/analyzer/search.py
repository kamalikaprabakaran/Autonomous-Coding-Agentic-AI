"""Ripgrep code search with python fallback."""

import json
import os
import subprocess
from pathlib import Path

from backend.app.models.analyzer import SearchResult
from backend.app.services.analyzer.config import MAX_FILE_SIZE
from backend.app.services.analyzer.discovery import is_binary, is_ignored, resolve_safe_path


def search_code(repo_path: str, query: str) -> list[SearchResult]:
    """Search for the query string inside non-ignored repository files.

    First attempts to use ripgrep for speed. Falls back to manual Python iteration
    if ripgrep is unavailable.
    """
    base = Path(repo_path).resolve(strict=True)
    
    # Try ripgrep first
    try:
        cmd = ["rg", query, str(base), "--json", "--ignore-case"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode in (0, 1):
            return _parse_ripgrep_output(result.stdout, base)
    except FileNotFoundError:
        # ripgrep not installed, gracefully fallback to python search
        pass

    # Python fallback
    return _python_fallback_search(base, query)


def _parse_ripgrep_output(stdout: str, base: Path) -> list[SearchResult]:
    """Parse JSON stream output from ripgrep."""
    results = []
    for line in stdout.splitlines():
        if not line.strip():
            continue
        try:
            data = json.loads(line)
            if data.get("type") == "match":
                match_data = data["data"]
                file_path = match_data["path"]["text"]
                line_number = match_data["line_number"]
                matching_line = match_data["lines"]["text"].rstrip("\n")
                
                # Check bounds for safety, even if rg returns it
                try:
                    resolve_safe_path(str(base), file_path)
                    
                    # Store as relative path
                    rel_path = Path(file_path).relative_to(base).as_posix()
                    
                    results.append(SearchResult(
                        file_path=rel_path,
                        line_number=line_number,
                        matching_line=matching_line.strip()
                    ))
                except Exception:
                    pass
        except json.JSONDecodeError:
            continue
    return results


def _python_fallback_search(base: Path, query: str) -> list[SearchResult]:
    """Fallback search using Python os.walk for systems without ripgrep."""
    results = []
    query_lower = query.lower()

    for root, dirs, filenames in os.walk(base, followlinks=False):
        current_root = Path(root)
        dirs[:] = [d for d in dirs if not is_ignored(current_root / d)]
        
        for name in filenames:
            file_path = current_root / name
            if is_ignored(file_path):
                continue
                
            try:
                if file_path.stat().st_size > MAX_FILE_SIZE:
                    continue
                if is_binary(file_path):
                    continue
                    
                with open(file_path, "r", encoding="utf-8") as f:
                    for line_idx, line in enumerate(f):
                        if query_lower in line.lower():
                            rel_path = file_path.relative_to(base).as_posix()
                            results.append(SearchResult(
                                file_path=rel_path,
                                line_number=line_idx + 1,
                                matching_line=line.strip()
                            ))
            except Exception:
                # Silently ignore inaccessible or unreadable files in fallback
                pass

    return results
