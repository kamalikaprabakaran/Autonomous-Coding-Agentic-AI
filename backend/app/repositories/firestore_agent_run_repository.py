"""Firestore-backed agent run repository."""

from typing import Optional
from backend.app.models.agent_run import AgentRun
from backend.app.repositories.base import AgentRunRepositoryProtocol
from backend.app.firebase.client import get_firestore_client
from backend.app.firebase.exceptions import FirebaseUnavailableError

class FirestoreAgentRunRepository(AgentRunRepositoryProtocol):
    """Store agent runs in Cloud Firestore."""

    def __init__(self, collection_name: str = "agent_runs"):
        self.collection_name = collection_name

    def _get_collection(self):
        try:
            return get_firestore_client().collection(self.collection_name)
        except Exception as e:
            raise FirebaseUnavailableError(f"Failed to access Firestore: {e}")

    def add(self, run: AgentRun) -> AgentRun:
        """Persist an agent run and return it."""
        doc_ref = self._get_collection().document(run.id)
        doc_ref.set(run.model_dump(mode='json'))
        return run

    def get(self, run_id: str) -> Optional[AgentRun]:
        """Return an agent run by id, or ``None`` if not found."""
        doc_ref = self._get_collection().document(run_id)
        doc = doc_ref.get()
        if doc.exists:
            return AgentRun.model_validate(doc.to_dict())
        return None

    def list_all(self) -> list[AgentRun]:
        """Return all stored agent runs."""
        docs = self._get_collection().stream()
        return [AgentRun.model_validate(doc.to_dict()) for doc in docs]

    def list_by_owner(self, owner_id: str) -> list[AgentRun]:
        """Return agent runs owned by the specified user."""
        docs = self._get_collection().where("owner_id", "==", owner_id).stream()
        return [AgentRun.model_validate(doc.to_dict()) for doc in docs]
