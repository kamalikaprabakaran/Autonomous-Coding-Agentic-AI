"""Code search tooling."""

from typing import Type
from pydantic import BaseModel

from backend.app.models.tools import ToolResult, SearchCodeInput
from backend.app.tools.base import BaseTool
from backend.app.services.analyzer.search import search_code
from backend.app.services.analyzer.discovery import SecurityError


class SearchCodeTool(BaseTool):
    """Search for string patterns within repository text files."""
    name = "search_code"
    description = "Search for exact string matches inside repository code files."
    input_schema: Type[BaseModel] = SearchCodeInput

    def execute(self, repo_path: str, args: dict) -> ToolResult:
        input_data = self.input_schema(**args)
        
        try:
            results = search_code(repo_path, input_data.query)
            data = [r.model_dump() for r in results]
            return ToolResult(success=True, data=data)
            
        except SecurityError as e:
            return ToolResult(success=False, error=f"Security violation: {str(e)}")
        except FileNotFoundError:
            # Typically if repo_path doesn't exist
            return ToolResult(success=False, error="Repository path does not exist.")
        except Exception as e:
            return ToolResult(success=False, error=str(e))
