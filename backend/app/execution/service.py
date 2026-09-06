"""Execution REST service layer."""

from backend.app.models.execution import ExecutionRequest, ExecutionResult
from backend.app.execution.docker_executor import DockerExecutor

class ExecutionService:
    """Provides application-layer sandboxed command execution."""
    
    def __init__(self, executor: DockerExecutor = None):
        self.executor = executor or DockerExecutor()
        
    def execute_command(self, request: ExecutionRequest) -> ExecutionResult:
        """Runs the command requested enforcing business rules before reaching docker."""
        if not request.command or not request.command.strip():
             return ExecutionResult(success=False, error="Command cannot be empty.")
             
        # Call the underlying secure docker executor.
        # Note: the executor automatically enforces file bounds via resolve_safe_path
        return self.executor.execute(request)
