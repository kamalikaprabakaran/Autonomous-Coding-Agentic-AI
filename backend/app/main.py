"""FastAPI application entry point.

Provides a factory function ``create_app`` that builds the application with
lifespan-managed logging, Phase 1 API routers, and a ``/health`` endpoint.
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api import agent_router, projects_router, tasks_router
from backend.app.core.config import get_settings
from backend.app.core.exceptions import NotFoundError, not_found_handler
from backend.app.core.logging import setup_logging
from backend.app.repositories.agent_run_repository import InMemoryAgentRunRepository
from backend.app.repositories.project_repository import InMemoryProjectRepository
from backend.app.repositories.task_repository import InMemoryTaskRepository
from backend.app.services.agent_run_service import AgentRunService
from backend.app.services.project_service import ProjectService
from backend.app.services.task_service import TaskService


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: set up logging on startup, tear down on shutdown."""
    settings = get_settings()
    setup_logging(settings.LOG_LEVEL)
    logger.info(
        "Starting %s v%s", settings.APP_NAME, settings.APP_VERSION
    )
    yield
    logger.info("Shutting down %s", settings.APP_NAME)


def create_app() -> FastAPI:
    """Build and return the FastAPI application instance.

    Each call creates fresh repository and service instances, ensuring
    test isolation when ``create_app()`` is called per-test in conftest.
    """
    settings = get_settings()

    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    # ── CORS Middleware ──────────────────────────────────────────────
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Dependency injection via app.state ───────────────────────────
    project_repo = InMemoryProjectRepository()
    task_repo = InMemoryTaskRepository()
    agent_run_repo = InMemoryAgentRunRepository()

    project_service = ProjectService(project_repo)
    task_service = TaskService(task_repo, project_service)
    agent_run_service = AgentRunService(agent_run_repo)
    
    from backend.app.services.analyzer.analyzer import RepositoryAnalyzer
    from backend.app.execution.service import ExecutionService
    repository_analyzer = RepositoryAnalyzer()
    execution_service = ExecutionService()

    application.state.project_service = project_service
    application.state.task_service = task_service
    application.state.agent_run_service = agent_run_service
    application.state.repository_analyzer = repository_analyzer
    application.state.execution_service = execution_service

    # ── Exception handlers ───────────────────────────────────────────
    application.add_exception_handler(NotFoundError, not_found_handler)

    # ── Phase 0 health endpoint ──────────────────────────────────────
    @application.get("/health", tags=["Health"])
    async def health_check() -> dict[str, str]:
        """Return application health status."""
        return {"status": "healthy"}

    # ── Phase 1 API routers ──────────────────────────────────────────
    application.include_router(projects_router)
    application.include_router(tasks_router)
    application.include_router(agent_router)
    
    from backend.app.api import execution_router
    application.include_router(execution_router)

    return application


app = create_app()
