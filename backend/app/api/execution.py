"""Execution Sandbox API router."""

from fastapi import APIRouter, Depends, HTTPException, Request
import logging

from backend.app.models.execution import ExecutionRequest, ExecutionResult
from backend.app.execution.service import ExecutionService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/execution",
    tags=["execution"]
)

@router.post("/run", response_model=ExecutionResult)
async def run_execution(req: ExecutionRequest, request: Request):
    """Executes a command safely inside a Sandbox mapping to the given repository path."""
    # Resolve service strictly avoiding globals
    service: ExecutionService = request.app.state.execution_service
    
    try:
        logger.info(f"Dispatching Execution sandbox for '{req.repository_path}': `{req.command}`")
        result = service.execute_command(req)
        return result
    except Exception as e:
        logger.error(f"Unexpected execution container failure: {e}")
        # Map internal errors into safe 500 REST responses
        raise HTTPException(status_code=500, detail="Sandbox initialization failed")
