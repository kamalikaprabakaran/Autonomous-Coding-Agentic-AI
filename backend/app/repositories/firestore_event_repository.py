"""Firestore-backed and In-Memory Event Repositories."""

from backend.app.models.event import AgentEvent
from backend.app.repositories.base import EventRepositoryProtocol


class InMemoryEventRepository(EventRepositoryProtocol):
    """In-memory backend for observability testing."""
    
    def __init__(self):
        self._events: dict[str, AgentEvent] = {}
        
    def add(self, event: AgentEvent) -> AgentEvent:
        self._events[event.id] = event
        return event
        
    def list_by_run(self, run_id: str) -> list[AgentEvent]:
        # Return sorted by timestamp exactly
        results = [e for e in self._events.values() if e.run_id == run_id]
        results.sort(key=lambda x: x.timestamp)
        return results


class FirestoreEventRepository(EventRepositoryProtocol):
    """Firestore backend for observability events."""
    
    def __init__(self, db_client):
        self._db = db_client
        self._collection = "events"
        
    def add(self, event: AgentEvent) -> AgentEvent:
        doc_ref = self._db.collection(self._collection).document(event.id)
        doc_ref.set(event.model_dump(mode="json"))
        return event
        
    def list_by_run(self, run_id: str) -> list[AgentEvent]:
        query = self._db.collection(self._collection).where("run_id", "==", run_id)
        docs = query.stream()
        results = [AgentEvent.model_validate(doc.to_dict()) for doc in docs]
        results.sort(key=lambda x: x.timestamp)
        return results
