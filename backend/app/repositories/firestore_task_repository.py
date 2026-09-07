"""Firestore-backed task repository."""

from typing import Optional
from backend.app.models.task import CodingTask
from backend.app.repositories.base import TaskRepositoryProtocol
from backend.app.firebase.client import get_firestore_client
from backend.app.firebase.exceptions import FirebaseUnavailableError

class FirestoreTaskRepository(TaskRepositoryProtocol):
    """Store tasks in Cloud Firestore."""

    def __init__(self, collection_name: str = "tasks"):
        self.collection_name = collection_name

    def _get_collection(self):
        try:
            return get_firestore_client().collection(self.collection_name)
        except Exception as e:
            raise FirebaseUnavailableError(f"Failed to access Firestore: {e}")

    def add(self, task: CodingTask) -> CodingTask:
        """Persist a task and return it."""
        doc_ref = self._get_collection().document(task.id)
        # Using json serialization pattern for enums and datetimes natively handled by Pydantic
        doc_ref.set(task.model_dump(mode='json'))
        return task

    def get(self, task_id: str) -> Optional[CodingTask]:
        """Return a task by id, or ``None`` if not found."""
        doc_ref = self._get_collection().document(task_id)
        doc = doc_ref.get()
        if doc.exists:
            return CodingTask.model_validate(doc.to_dict())
        return None

    def list_all(self) -> list[CodingTask]:
        """Return all stored tasks."""
        docs = self._get_collection().stream()
        return [CodingTask.model_validate(doc.to_dict()) for doc in docs]

    def list_by_owner(self, owner_id: str) -> list[CodingTask]:
        """Return tasks owned by the specified user."""
        # Using string matching for firestore field equality
        docs = self._get_collection().where("owner_id", "==", owner_id).stream()
        return [CodingTask.model_validate(doc.to_dict()) for doc in docs]
