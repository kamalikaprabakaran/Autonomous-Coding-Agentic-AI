"""Firestore-backed project repository."""

from typing import Optional
from backend.app.models.project import Project
from backend.app.repositories.base import ProjectRepositoryProtocol
from backend.app.firebase.client import get_firestore_client
from backend.app.firebase.exceptions import FirebaseUnavailableError

class FirestoreProjectRepository(ProjectRepositoryProtocol):
    """Store projects in Cloud Firestore."""

    def __init__(self, collection_name: str = "projects"):
        self.collection_name = collection_name

    def _get_collection(self):
        try:
            return get_firestore_client().collection(self.collection_name)
        except Exception as e:
            raise FirebaseUnavailableError(f"Failed to access Firestore: {e}")

    def add(self, project: Project) -> Project:
        """Persist a project and return it."""
        doc_ref = self._get_collection().document(project.id)
        doc_ref.set(project.model_dump())
        return project

    def get(self, project_id: str) -> Optional[Project]:
        """Return a project by id, or ``None`` if not found."""
        doc_ref = self._get_collection().document(project_id)
        doc = doc_ref.get()
        if doc.exists:
            return Project.model_validate(doc.to_dict())
        return None

    def list_all(self) -> list[Project]:
        """Return all stored projects (not recommended for large collections)."""
        docs = self._get_collection().stream()
        return [Project.model_validate(doc.to_dict()) for doc in docs]

    def list_by_owner(self, owner_id: str) -> list[Project]:
        """Return projects owned by the specified user."""
        docs = self._get_collection().where("owner_id", "==", owner_id).stream()
        return [Project.model_validate(doc.to_dict()) for doc in docs]
