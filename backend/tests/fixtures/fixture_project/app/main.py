import os
from typing import List

from . import utils
import sys

def standalone_function(x: int, y: int) -> int:
    """This is a standalone function."""
    return x + y

class UserService:
    """Service for users."""
    
    def __init__(self, db_conn):
        self.db = db_conn
        
    def get_user(self, user_id: str):
        # A searchable word: UNIQUE_SEARCH_TERM
        return {"id": user_id, "name": "Test"}
        
    def _private_method(self):
        pass
