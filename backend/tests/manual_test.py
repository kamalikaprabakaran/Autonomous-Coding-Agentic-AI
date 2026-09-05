import json
from backend.app.tools.registry import ToolRegistry
from backend.app.tools.file_tools import (
    ListFilesTool, ReadFileTool, WriteFileTool, EditFileTool, GetFileInfoTool
)
from backend.app.tools.search_tools import SearchCodeTool

def run_checks():
    reg = ToolRegistry()
    reg.register(ListFilesTool())
    reg.register(ReadFileTool())
    reg.register(WriteFileTool())
    reg.register(EditFileTool())
    reg.register(GetFileInfoTool())
    reg.register(SearchCodeTool())
    
    print("Tools registered:", [t["name"] for t in reg.list_tools()])
    
    repo_path = "backend/tests/fixtures/fixture_project"
    
    # 1. list_files
    print("\n[list_files]")
    r = reg.get("list_files").execute(repo_path, {})
    print("Success:", r.success, "| Found files:", len(r.data))
    
    # 2. get_file_info
    print("\n[get_file_info]")
    r = reg.get("get_file_info").execute(repo_path, {"path": "app"})
    print("Success:", r.success, "| Info:", r.data)
    
    # 3. write_file
    print("\n[write_file]")
    r = reg.get("write_file").execute(repo_path, {"path": "app/manual_test.txt", "content": "Manual validation content!"})
    print("Success:", r.success, "| Result:", r.data)
    
    # 4. read_file
    print("\n[read_file]")
    r = reg.get("read_file").execute(repo_path, {"path": "app/manual_test.txt"})
    print("Success:", r.success, "| Content:", r.data["content"])
    
    # 5. edit_file
    print("\n[edit_file]")
    r = reg.get("edit_file").execute(repo_path, {"path": "app/manual_test.txt", "old_text": "validation", "new_text": "EDITED"})
    print("Success:", r.success, "| Result:", r.data)
    
    # 6. search_code
    print("\n[search_code]")
    r = reg.get("search_code").execute(repo_path, {"query": "EDITED"})
    print("Success:", r.success, "| Matches:", len(r.data))
    
    # 7. path traversal
    print("\n[path_traversal_test]")
    r = reg.get("read_file").execute(repo_path, {"path": "../../windows/system32"})
    print("Success:", r.success, "| Error:", r.error)

if __name__ == "__main__":
    run_checks()
