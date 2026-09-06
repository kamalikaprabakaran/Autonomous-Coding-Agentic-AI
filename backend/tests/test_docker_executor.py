"""Docker Executor SDK tests handling internal integration fallbacks properly."""

import pytest
from unittest.mock import MagicMock, patch
from backend.app.execution.docker_executor import DockerExecutor
from backend.app.models.execution import ExecutionRequest
from backend.app.services.analyzer.discovery import resolve_safe_path

# Pytest checks whether we skip real Docker tests if disconnected.
import docker
try:
    client = docker.from_env()
    client.ping()
    DOCKER_AVAILABLE = True
except Exception:
    DOCKER_AVAILABLE = False


@pytest.fixture
def test_repo_path(tmp_path):
    d = tmp_path / "repo"
    d.mkdir()
    (d / "script.py").write_text("print('Hello from offline sandbox!')")
    
    # Create an invalid syntax script to test non-zero exits
    (d / "bad.py").write_text("import missing_package\nprint(1/0)")
    return str(d)


@patch("backend.app.execution.docker_executor.docker.from_env")
def test_executor_successful_command(mock_docker_env, test_repo_path):
    """Executes a simple python code inside the sandbox container safely."""
    # Build complete execution mocking layers
    mock_client = MagicMock()
    mock_container = MagicMock()
    mock_docker_env.return_value = mock_client
    mock_client.containers.run.return_value = mock_container
    
    mock_container.wait.return_value = {"StatusCode": 0}
    mock_container.logs.side_effect = [b"Hello from offline sandbox!", b""]
    
    executor = DockerExecutor()
    req = ExecutionRequest(
        repository_path=test_repo_path, 
        command="python script.py"
    )
    
    res = executor.execute(req)
    
    assert res.success is True
    assert res.exit_code == 0
    assert "Hello from offline sandbox!" in res.stdout
    assert res.timed_out is False


@patch("backend.app.execution.docker_executor.docker.from_env")
def test_executor_failing_command(mock_docker_env, test_repo_path):
    """Execution trapping non-zero exit codes."""
    mock_client = MagicMock()
    mock_container = MagicMock()
    mock_docker_env.return_value = mock_client
    mock_client.containers.run.return_value = mock_container
    
    # A crash simulation
    mock_container.wait.return_value = {"StatusCode": 1}
    mock_container.logs.side_effect = [b"", b"Traceback error simulation"]

    executor = DockerExecutor()
    req = ExecutionRequest(repository_path=test_repo_path, command="python bad.py")
    
    res = executor.execute(req)
    
    assert res.success is False # It executed gracefully but failed internally
    assert res.exit_code != 0
    assert "Traceback" in res.stderr


@patch("backend.app.execution.docker_executor.docker.from_env")
def test_executor_timeout(mock_docker_env, test_repo_path):
    """Test Docker bounding execution timeout gracefully stopping the command."""
    mock_client = MagicMock()
    mock_container = MagicMock()
    mock_docker_env.return_value = mock_client
    mock_client.containers.run.return_value = mock_container
    
    # Raise timeout condition natively
    mock_container.wait.side_effect = Exception("Read timed out")

    executor = DockerExecutor()
    
    # A sleep command simulated in Python
    req = ExecutionRequest(
        repository_path=test_repo_path, 
        command="python -c \"import time; time.sleep(10)\"",
        timeout_seconds=2 # Trap it early
    )
    
    res = executor.execute(req)
    # The SDK forces a read timeout mapped safely
    assert res.success is False
    assert res.timed_out is True
    assert "timeout" in res.error.lower()


def test_executor_invalid_repo():
    """Testing path bound traps gracefully propagating early."""
    executor = DockerExecutor()
    req = ExecutionRequest(
        repository_path="/var/does/not/exist/999", 
        command="ls"
    )
    
    res = executor.execute(req)
    assert res.success is False
    assert "does not exist" in res.error
