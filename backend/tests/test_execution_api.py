"""Unit tests mapping API endpoint parameters and integration endpoints."""
from httpx import AsyncClient
import pytest
from unittest.mock import MagicMock
from backend.app.models.execution import ExecutionResult

@pytest.mark.asyncio
async def test_api_run_success(client: AsyncClient, app):
    """API successfully parses schema and invokes the service layer correctly"""
    mock_executor = MagicMock()
    mock_executor.execute_command.return_value = ExecutionResult(success=True, exit_code=0, stdout="OK")
    app.state.execution_service = mock_executor
    
    response = await client.post(
        "/execution/run",
        json={"repository_path": "/var/mock/repo", "command": "python script.py"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["stdout"] == "OK"
    assert mock_executor.execute_command.called


@pytest.mark.asyncio
async def test_api_run_service_failure(client: AsyncClient, app):
    """API traps raw system exceptions replacing them with 500 headers"""
    mock_executor = MagicMock()
    mock_executor.execute_command.side_effect = Exception("System blew up natively")
    app.state.execution_service = mock_executor
    
    response = await client.post(
        "/execution/run",
        json={"repository_path": "/var/mock/repo", "command": "python script.py"}
    )
    
    assert response.status_code == 500
    assert "Sandbox initialization failed" in response.json()["detail"]
