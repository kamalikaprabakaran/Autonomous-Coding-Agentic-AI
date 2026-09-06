"""Tests for the Execution models constraints."""

from backend.app.models.execution import ExecutionRequest, ExecutionResult

def test_execution_request_fields():
    """Verify execution inputs enforce bounds."""
    req = ExecutionRequest(repository_path="/foo/bar", command="pytest -v")
    
    assert req.repository_path == "/foo/bar"
    assert req.command == "pytest -v"
    # Defends against unsafe defaults by forcing standard resolutions inside the Executor
    assert req.timeout_seconds is None


def test_execution_result_fields():
    """Verify standard execution dumps."""
    res = ExecutionResult(success=True, exit_code=0, stdout="Hello", duration_seconds=1.2)
    assert res.success is True
    assert res.timed_out is False
    assert res.exit_code == 0
    assert "Hello" in res.stdout
