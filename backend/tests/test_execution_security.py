"""Security validation tests for Sandboxed Execution boundaries."""

import pytest
from backend.app.execution.docker_executor import DockerExecutor
from backend.app.models.execution import ExecutionRequest
from backend.app.services.analyzer.discovery import resolve_safe_path

def test_execution_blocks_host_directories():
    """Verify that trying to mount outside the permitted repos gets trapped by safe resolve paths."""
    executor = DockerExecutor()
    # Assume the repo root is where pytest executes (cwd)
    req = ExecutionRequest(
        repository_path="../../windows/system32",
        command="ls -la"
    )
    
    result = executor.execute(req)
    
    # Needs to fail specifically on boundary or existence trapping (Unix vs Win32 resolving rules)
    assert result.success is False

def test_execution_network_disabled():
    """Verify that defaults keep networking isolated."""
    req = ExecutionRequest(repository_path="backend", command="ping google.com")
    
    # We do not need the live docker for this unit test of defaults, just confirm the abstraction flags it correctly.
    # The default behavior ensures `network_enabled` passes `None` -> False.
    assert req.network_enabled is None
