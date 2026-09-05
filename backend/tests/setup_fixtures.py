import os
from pathlib import Path

FIXTURE_DIR = Path("backend/tests/fixtures/fixture_project")

def create_fixture():
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Ignored dirs
    (FIXTURE_DIR / ".git").mkdir(exist_ok=True)
    (FIXTURE_DIR / ".git" / "config").write_text("[core]\n\trepositoryformatversion = 0\n")
    
    (FIXTURE_DIR / "__pycache__").mkdir(exist_ok=True)
    (FIXTURE_DIR / "__pycache__" / "test.cpython-310.pyc").write_bytes(b"\x00\x01\x02")
    
    (FIXTURE_DIR / "node_modules").mkdir(exist_ok=True)
    (FIXTURE_DIR / "node_modules" / "some_pkg.js").write_text("console.log('hi');")
    
    # 2. Python files
    app_dir = FIXTURE_DIR / "app"
    app_dir.mkdir(exist_ok=True)
    
    (app_dir / "__init__.py").write_text('"""App init."""\n')
    
    main_content = '''import os
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
'''
    (app_dir / "main.py").write_text(main_content)
    
    # 3. Malformed python
    broken_content = '''def broken_function(
    return "This syntax is invalid"
'''
    (app_dir / "broken.py").write_text(broken_content)
    
    # 4. Large file
    # Config max file size is 1MB. We'll write 1.1MB of '0's.
    with open(FIXTURE_DIR / "huge.py", "w") as f:
        f.write("0" * int(1.1 * 1024 * 1024))
        
    # 5. Binary file
    with open(FIXTURE_DIR / "image.png", "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00")
        
    # 5b. Binary Python file
    with open(app_dir / "binary_test.py", "wb") as f:
        f.write(b"\x00\x00\x00\x00")
        
    # 6. Another sub-folder
    tests_dir = FIXTURE_DIR / "tests"
    tests_dir.mkdir(exist_ok=True)
    (tests_dir / "test_main.py").write_text('def test_dummy():\n    assert True\n')
    
    print("Fixture created.")
    
if __name__ == "__main__":
    create_fixture()
