"""Central repository analyzer orchestration."""

from collections import Counter
from pathlib import Path

from backend.app.models.analyzer import DirectoryNode, FileInfo, RepositoryAnalysis, SearchResult
from backend.app.services.analyzer.discovery import build_file_tree, is_binary, is_ignored, list_files, resolve_safe_path
from backend.app.services.analyzer.parser import analyze_python_file
from backend.app.services.analyzer.search import search_code


class RepositoryAnalyzer:
    """Orchestrates file discovery, code search, and python parsing."""

    def list_files(self, repository_path: str) -> list[FileInfo]:
        """List all non-ignored files in the repository."""
        return list_files(repository_path)

    def build_file_tree(self, repository_path: str) -> DirectoryNode:
        """Construct the directory structure of the repository."""
        return build_file_tree(repository_path)

    def search_code(self, repository_path: str, query: str) -> list[SearchResult]:
        """Search across non-ignored source files for a query."""
        return search_code(repository_path, query)
        
    def resolve_safe_path(self, repository_path: str, target: str) -> Path:
        """Resolve a path safely within the boundaries."""
        return resolve_safe_path(repository_path, target)

    def analyze_repository(self, repository_path: str) -> RepositoryAnalysis:
        """Run a full analysis of the repository."""
        # We need to compute total files, ignored files, extensions, classes, functions, etc.
        # list_files only returns non-ignored files, so we iterate manually for exact counts...
        # Wait, the simplest way is to fetch list_files(), and for ignored files we can iterate 
        # normally, but skipping deep traversal into ignored directories.
        
        base = Path(repository_path).resolve(strict=True)
        
        analyzed_files = 0
        ignored_files = 0
        skipped_large_files = 0
        skipped_binary_files = 0
        
        extensions_counter = Counter()
        
        python_files = 0
        classes_found = 0
        functions_found = 0
        errors = 0
        
        import os
        for root, dirs, filenames in os.walk(base, followlinks=False):
            current_root = Path(root)
            
            # Split out ignored directories so we don't traverse them, but count them
            # However, we only count the directory itself as ignored, not its children
            # to prevent massive inflation from node_modules.
            valid_dirs = []
            for d in dirs:
                if is_ignored(current_root / d):
                    ignored_files += 1
                else:
                    valid_dirs.append(d)
            dirs[:] = valid_dirs
            
            for name in filenames:
                file_path = current_root / name
                if is_ignored(file_path):
                    ignored_files += 1
                    continue
                    
                analyzed_files += 1
                extensions_counter[file_path.suffix.lower()] += 1
                
                # Further analysis for python files
                if file_path.suffix.lower() == ".py":
                    python_files += 1
                    rel_path = file_path.relative_to(base).as_posix()
                    
                    analysis = analyze_python_file(file_path, rel_path)
                    
                    if analysis.error == "File size exceeds limit":
                        skipped_large_files += 1
                    elif analysis.error == "File is binary":
                        skipped_binary_files += 1
                    elif not analysis.success:
                        errors += 1
                    else:
                        classes_found += len(analysis.classes)
                        functions_found += len(analysis.functions)
                        # Methods are nested inside classes, but we only count top-level classes/functions
                        # per the requirement for summary. (We could sum them, but sticking to classes/functions).

        return RepositoryAnalysis(
            repository_path=str(base),
            total_files=analyzed_files + ignored_files,
            analyzed_files=analyzed_files,
            ignored_files=ignored_files,
            python_files=python_files,
            extensions=dict(extensions_counter),
            classes_found=classes_found,
            functions_found=functions_found,
            errors=errors,
            skipped_large_files=skipped_large_files,
            skipped_binary_files=skipped_binary_files
        )
