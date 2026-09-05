"""Domain models for Repository Intelligence Analysis."""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class FileInfo(BaseModel):
    """Basic metadata for a discovered file."""

    path: str
    name: str
    extension: str
    size: int
    type: Literal["file", "directory"] = "file"


class DirectoryNode(BaseModel):
    """Represents a node in the repository file tree."""

    name: str
    type: Literal["file", "directory"]
    path: Optional[str] = None
    children: Optional[list["DirectoryNode"]] = None


class SearchResult(BaseModel):
    """Result of a code search query."""

    file_path: str
    line_number: int
    matching_line: str


class FunctionInfo(BaseModel):
    """Properties of a parsed Python function."""

    name: str
    args: list[str]
    start_line: int
    end_line: int


class MethodInfo(BaseModel):
    """Properties of a parsed Python method."""

    name: str
    args: list[str]
    start_line: int
    end_line: int


class ClassInfo(BaseModel):
    """Properties of a parsed Python class."""

    name: str
    methods: list[MethodInfo]
    start_line: int
    end_line: int


class ImportInfo(BaseModel):
    """Properties of a parsed Python import statement."""

    module: str
    names: list[str]
    line_number: int


class PythonFileAnalysis(BaseModel):
    """Structured analysis of a specific Python file."""

    success: bool
    file_path: str
    classes: list[ClassInfo] = Field(default_factory=list)
    functions: list[FunctionInfo] = Field(default_factory=list)
    imports: list[ImportInfo] = Field(default_factory=list)
    error: Optional[str] = None


class RepositoryAnalysis(BaseModel):
    """Summary representation of a software repository."""

    repository_path: str
    total_files: int
    analyzed_files: int
    ignored_files: int
    python_files: int
    extensions: dict[str, int]
    classes_found: int
    functions_found: int
    errors: int
    skipped_large_files: int
    skipped_binary_files: int

DirectoryNode.model_rebuild()
