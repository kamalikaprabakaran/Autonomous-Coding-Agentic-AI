"""Base components for agent tools."""

from abc import ABC, abstractmethod
from typing import Type
from pydantic import BaseModel

from backend.app.models.tools import ToolResult


class BaseTool(ABC):
    """Abstract base class for all tools."""

    name: str = ""
    description: str = ""
    input_schema: Type[BaseModel]

    @abstractmethod
    def execute(self, repo_path: str, args: dict) -> ToolResult:
        """Execute the tool within the given repository bounds.
        
        Args:
            repo_path (str): The absolute path to the root of the sandbox repository.
            args (dict): The tool arguments to unpack.
            
        Returns:
            ToolResult: The structured outcome of the execution.
        """
        pass
