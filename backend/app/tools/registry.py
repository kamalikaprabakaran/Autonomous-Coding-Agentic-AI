"""Registry for managing and discovering agent tools."""

from typing import Type, Optional
from backend.app.tools.base import BaseTool
import time
from backend.app.models.event import AgentEvent, AgentEventType
from backend.app.repositories.base import EventRepositoryProtocol
from backend.app.models.tools import ToolResult


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
        
    def execute_tool(
        self, 
        name: str, 
        repo_path: str, 
        args: dict, 
        event_repo: Optional[EventRepositoryProtocol] = None, 
        run_id: Optional[str] = None
    ) -> ToolResult:
        """Execute a tool while emitting structured monotonic observability events."""
        tool = self.get(name)
        if not tool:
            return ToolResult(success=False, output=f"Unknown tool: {name}", error=f"Tool {name} not registered")
            
        start_t = time.monotonic()
        if event_repo and run_id:
            try:
                # Sanitize arguments to prevent secrets or massive string blobs
                safe_args = args.copy()
                for key in ["content", "old_text", "new_text", "code_snippet"]:
                    if key in safe_args and isinstance(safe_args[key], str):
                        safe_args[key] = "<redacted_or_truncated>"
                        
                event_repo.add(AgentEvent(
                    run_id=run_id, event_type=AgentEventType.TOOL_CALLED,
                    tool_name=name, metadata={"args": str(safe_args)}
                ))
            except Exception:
                pass
                
        try:
            result = tool.execute(repo_path, args)
            dur = time.monotonic() - start_t
            if event_repo and run_id:
                try:
                    event_repo.add(AgentEvent(
                        run_id=run_id, event_type=AgentEventType.TOOL_COMPLETED,
                        tool_name=name, status="success" if result.success else "failed",
                        error=result.error, duration_seconds=dur
                    ))
                except Exception:
                    pass
            return result
        except Exception as e:
            dur = time.monotonic() - start_t
            if event_repo and run_id:
                try:
                    event_repo.add(AgentEvent(
                        run_id=run_id, event_type=AgentEventType.TOOL_COMPLETED,
                        tool_name=name, status="failed",
                        error=str(e), duration_seconds=dur
                    ))
                except Exception:
                    pass
            return ToolResult(success=False, output="", error=f"System exception: {str(e)}")
