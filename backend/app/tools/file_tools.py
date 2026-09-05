"""File manipulation tools."""

import datetime
from pathlib import Path
from typing import Type
from pydantic import BaseModel

from backend.app.models.tools import (
    ToolResult,
    ListFilesInput,
    ReadFileInput,
    WriteFileInput,
    EditFileInput,
    GetFileInfoInput
)
from backend.app.tools.base import BaseTool
from backend.app.services.analyzer.discovery import list_files, resolve_safe_path, is_binary, SecurityError
from backend.app.services.analyzer.config import MAX_FILE_SIZE


class ListFilesTool(BaseTool):
    """List files in the workspace matching intelligence ignores."""
    name = "list_files"
    description = "Recursively list all non-ignored files in the repository."
    input_schema: Type[BaseModel] = ListFilesInput

    def execute(self, repo_path: str, args: dict) -> ToolResult:
        try:
            # We don't explicitly need to validate an arg, but we invoke discovery
            files = list_files(repo_path)
            data = [f.model_dump() for f in files]
            return ToolResult(success=True, data=data)
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class ReadFileTool(BaseTool):
    """Read a text file securely within bounds."""
    name = "read_file"
    description = "Read the contents of a permitted text file."
    input_schema: Type[BaseModel] = ReadFileInput

    def execute(self, repo_path: str, args: dict) -> ToolResult:
        input_data = self.input_schema(**args)
        
        try:
            target = resolve_safe_path(repo_path, input_data.path)
            
            if not target.exists() or not target.is_file():
                return ToolResult(success=False, error="File not found or is not a file.")
            
            if target.stat().st_size > MAX_FILE_SIZE:
                return ToolResult(success=False, error="File is too large to read.")
                
            if is_binary(target):
                return ToolResult(success=False, error="Cannot read a binary file.")
                
            # Assume utf-8, ignore errors
            content = target.read_text(encoding="utf-8", errors="ignore")
            return ToolResult(success=True, data={"content": content})
            
        except SecurityError as e:
            return ToolResult(success=False, error=f"Security violation: {str(e)}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class WriteFileTool(BaseTool):
    """Write or overwrite a file securely."""
    name = "write_file"
    description = "Create a new file or replace the contents of an existing file."
    input_schema: Type[BaseModel] = WriteFileInput

    def execute(self, repo_path: str, args: dict) -> ToolResult:
        input_data = self.input_schema(**args)
        
        try:
            # Ensure safe bounds
            target = resolve_safe_path(repo_path, input_data.path)
            
            is_overwrite = target.exists()
            if is_overwrite and not target.is_file():
                return ToolResult(success=False, error="Target exists but is not a file.")
                
            # Create parents safely if needed
            target.parent.mkdir(parents=True, exist_ok=True)
            
            target.write_text(input_data.content, encoding="utf-8")
            
            return ToolResult(
                success=True, 
                data={"status": "overwritten" if is_overwrite else "created", "path": input_data.path}
            )
            
        except SecurityError as e:
            return ToolResult(success=False, error=f"Security violation: {str(e)}")
        except PermissionError:
            return ToolResult(success=False, error="Permission denied when writing file.")
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class EditFileTool(BaseTool):
    """Edit an existing file cleanly without regex assumptions, requiring exact match."""
    name = "edit_file"
    description = "Perform a controlled modification of an existing file by replacing exact text."
    input_schema: Type[BaseModel] = EditFileInput

    def execute(self, repo_path: str, args: dict) -> ToolResult:
        input_data = self.input_schema(**args)
        
        try:
            target = resolve_safe_path(repo_path, input_data.path)
            
            if not target.exists() or not target.is_file():
                return ToolResult(success=False, error="File not found.")
                
            if target.stat().st_size > MAX_FILE_SIZE:
                return ToolResult(success=False, error="File is too large to edit safely.")
                
            if is_binary(target):
                return ToolResult(success=False, error="Cannot edit a binary file.")
                
            content = target.read_text(encoding="utf-8", errors="ignore")
            
            old_text = input_data.old_text
            if not old_text:
                return ToolResult(success=False, error="old_text cannot be empty.")
                
            counts = content.count(old_text)
            if counts == 0:
                return ToolResult(success=False, error="Target text not found in file.")
            if counts > 1:
                return ToolResult(success=False, error=f"Ambiguous replacement: target text matches {counts} times.")
                
            new_content = content.replace(old_text, input_data.new_text)
            target.write_text(new_content, encoding="utf-8")
            
            return ToolResult(success=True, data={"status": "edited", "replacements": 1})
            
        except SecurityError as e:
            return ToolResult(success=False, error=f"Security violation: {str(e)}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class GetFileInfoTool(BaseTool):
    """Return metadata about a specific file or directory."""
    name = "get_file_info"
    description = "Retrieve metadata about a specific file or directory."
    input_schema: Type[BaseModel] = GetFileInfoInput

    def execute(self, repo_path: str, args: dict) -> ToolResult:
        input_data = self.input_schema(**args)
        
        try:
            target = resolve_safe_path(repo_path, input_data.path)
            
            if not target.exists():
                return ToolResult(success=False, error="Path not found.")
                
            stat = target.stat()
            is_dir = target.is_dir()
            
            metadata = {
                "path": str(target.relative_to(Path(repo_path).resolve(strict=True)).as_posix()),
                "name": target.name,
                "is_directory": is_dir,
                "size": stat.st_size if not is_dir else 0,
                "extension": target.suffix.lower() if not is_dir else "",
                "modified": datetime.datetime.fromtimestamp(stat.st_mtime, tz=datetime.timezone.utc).isoformat()
            }
            
            if not is_dir:
                metadata["is_binary"] = is_binary(target)
                
            return ToolResult(success=True, data=metadata)
            
        except SecurityError as e:
            return ToolResult(success=False, error=f"Security violation: {str(e)}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))
