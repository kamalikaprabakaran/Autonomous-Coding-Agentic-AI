from backend.app.api.projects import router as projects_router
from backend.app.api.tasks import router as tasks_router
from backend.app.api.agent import router as agent_router
from backend.app.api.execution import router as execution_router

__all__ = [
    "projects_router",
    "tasks_router",
    "agent_router",
    "execution_router"
]
