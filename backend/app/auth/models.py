"""Auth domain models."""

from typing import Optional
from pydantic import BaseModel

class AuthenticatedUser(BaseModel):
    """Represents an application user authenticated via Firebase Auth."""
    
    uid: str
    email: Optional[str] = None
    email_verified: Optional[bool] = None
