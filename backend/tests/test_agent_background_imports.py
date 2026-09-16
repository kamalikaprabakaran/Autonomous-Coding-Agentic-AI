"""Regression tests for agent background execution imports."""

import pytest
from backend.app.api.agent import start_agent_run, execute_agent_background
from backend.app.models.agent_run import AgentRunStatus
from unittest.mock import MagicMock

def test_execute_agent_background_import_regression():
    """Verify that execute_agent_background successfully loads all tool abstractions without ImportError."""
    # We mock out the run_agent call inside the background dispatcher to isolate the import phase
    import backend.app.api.agent as agent_api
    
    # Store original
    original_run_agent = getattr(agent_api, "run_agent", None)
    if original_run_agent is None:
        try:
            from backend.app.agents.graph import run_agent as orig_ra
            original_run_agent = orig_ra
        except ImportError:
            pytest.fail("Cannot locate run_agent globally.")
            
    try:
        # Mock run_agent natively returning empty final state
        agent_api.run_agent = MagicMock(return_value={"final_status": "success", "iteration_count": 0, "errors": []})
        
        # Setup mocks
        request_mock = MagicMock()
        service_mock = MagicMock()
        run_mock = MagicMock()
        run_mock.id = "regression-test-id"
        run_mock.status = AgentRunStatus.PENDING
        run_mock.error_summary = None
        
        service_mock.get_run.return_value = run_mock
        request_mock.app.state.agent_run_service = service_mock
        request_mock.app.state.repository_analyzer = MagicMock()
        
        class MockExecutor:
            def execute(self, state):
                return {"execution_result": {"success": True}}
                
        request_mock.app.state.execution_service.executor = MockExecutor()
        request_mock.app.state.event_repository = MagicMock()
        
        # The execution shouldn't raise any ImportErrors (such as RipgrepSearchTool)
        execute_agent_background(run_id="regression-test-id", request=request_mock, task_desc="desc", repo_path=".")
        
        # Dump error summary explicitly if it fails
        assert run_mock.error_summary is None, f"Execution failed internally: {run_mock.error_summary}"
        assert run_mock.status == AgentRunStatus.COMPLETED
        
    except ImportError as e:
        pytest.fail(f"Regression detected: execute_agent_background imports structurally invalid components: {e}")
    finally:
        # Restore mock
        agent_api.run_agent = original_run_agent
