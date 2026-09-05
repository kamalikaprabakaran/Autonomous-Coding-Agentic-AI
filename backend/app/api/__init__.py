"""API route package."""

from backend.app.api.agent import router as agent_router
from backend.app.api.projects import router as projects_router
from backend.app.api.tasks import router as tasks_router

__all__ = [
    "agent_router",
    "projects_router",
    "tasks_router",
]
