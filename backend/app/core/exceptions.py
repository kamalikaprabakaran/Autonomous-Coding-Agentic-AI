"""Custom application exceptions and FastAPI exception handlers."""

from fastapi import Request
from fastapi.responses import JSONResponse


class NotFoundError(Exception):
    """Raised when a requested resource does not exist."""

    def __init__(self, resource: str, resource_id: str) -> None:
        self.resource = resource
        self.resource_id = resource_id
        super().__init__(f"{resource} with id '{resource_id}' not found")


async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    """Return a clean 404 JSON response for NotFoundError."""
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )
