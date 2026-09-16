import pytest
from backend.app.models.event import AgentEvent, AgentEventType
from backend.app.repositories.firestore_event_repository import InMemoryEventRepository

def test_in_memory_event_storage():
    """Verify the bounded persistence capabilities."""
    repo = InMemoryEventRepository()
    
    evt1 = AgentEvent(run_id="run-1", event_type=AgentEventType.RUN_STARTED)
    evt2 = AgentEvent(run_id="run-1", event_type=AgentEventType.RUN_COMPLETED, duration_seconds=5.5, status="success")
    evt3 = AgentEvent(run_id="run-2", event_type=AgentEventType.RUN_STARTED)
    
    repo.add(evt1)
    repo.add(evt2)
    repo.add(evt3)
    
    run_1_events = repo.list_by_run("run-1")
    assert len(run_1_events) == 2
    assert run_1_events[0].id == evt1.id
    assert run_1_events[1].duration_seconds == 5.5
    
    run_2_events = repo.list_by_run("run-2")
    assert len(run_2_events) == 1
    assert run_2_events[0].run_id == "run-2"
