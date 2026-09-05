"""Registry for managing and discovering agent tools."""

from typing import Type
from backend.app.tools.base import BaseTool


class ToolRegistry:
    """A registry for holding and fetching tool implementations."""
    
    def __init__(self):
        self._tools: dict[str, BaseTool] = {}
        
    def register(self, tool: BaseTool) -> None:
        """Register a tool instance."""
        if not tool.name:
            raise ValueError("Tool must have a valid 'name' attribute.")
        self._tools[tool.name] = tool
        
    def get(self, name: str) -> BaseTool | None:
        """Retrieve a specific tool by name."""
        return self._tools.get(name)
        
    def list_tools(self) -> list[dict]:
        """Return metadata for all registered tools."""
        return [
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.input_schema.model_json_schema()
            }
            for t in self._tools.values()
        ]
