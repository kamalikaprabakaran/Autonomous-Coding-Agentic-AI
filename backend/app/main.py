"""FastAPI application entry point.

Provides a factory function ``create_app`` that builds the application with
lifespan-managed logging and a ``/health`` endpoint.
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.app.core.config import get_settings
from backend.app.core.logging import setup_logging


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
    """Build and return the FastAPI application instance."""
    settings = get_settings()

    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    @application.get("/health")
    async def health_check() -> dict[str, str]:
        """Return application health status."""
        return {"status": "healthy"}

    return application


app = create_app()
