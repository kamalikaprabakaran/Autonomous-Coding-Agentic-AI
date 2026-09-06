import sys
import time
sys.path.append('d:/Autonomous Coding Agentic AI')
from backend.app.execution.docker_executor import DockerExecutor
from backend.app.models.execution import ExecutionRequest

executor = DockerExecutor()
assert executor.client is not None, "Docker is not available"
print("Docker connected successfully.")

def check(req, expected_success, expected_code=None, expected_timeout=False):
    res = executor.execute(req)
    print(f"[{req.command}] Success: {res.success}, Exit: {res.exit_code}, TimedOut: {res.timed_out}, Duration: {res.duration_seconds}")
    # print debug
    if res.stderr:
        print("STDERR:", res.stderr.strip())
    if res.stdout:
        print("STDOUT:", res.stdout.strip())
        
    assert res.success == expected_success, f"Expected success={expected_success}, got {res.success}"
    if expected_code is not None:
        assert res.exit_code == expected_code, f"Expected exit_code={expected_code}, got {res.exit_code}"
    assert res.timed_out == expected_timeout, f"Expected timed_out={expected_timeout}, got {res.timed_out}"
    return res

repo = 'd:/Autonomous Coding Agentic AI'

try:
    print("\nx-- Running A --x")
    req = ExecutionRequest(repository_path=repo, command="python -c \"print('sandbox-ok')\"")
    res_a = check(req, True, 0, False)
    assert "sandbox-ok" in res_a.stdout
    
    print("\nx-- Running B --x")
    req = ExecutionRequest(repository_path=repo, command="python -c \"raise SystemExit(2)\"")
    check(req, False, 2, False)
    
    print("\nx-- Running C --x")
    req = ExecutionRequest(repository_path=repo, command="python -c \"import time; time.sleep(10)\"", timeout_seconds=2)
    check(req, False, -1, True)
    
    print("\nx-- Running D --x")
    req = ExecutionRequest(repository_path=repo, command="python -c \"open('read_only_test.txt', 'w').write('test')\"")
    res_d = check(req, False, 1, False)
    assert "Read-only file system" in res_d.stderr or "Permission expected" in res_d.stderr or "OSError: [Errno 30]" in res_d.stderr
    
    print("\nx-- Running E --x")
    req = ExecutionRequest(repository_path=repo, command="python -c \"import urllib.request; urllib.request.urlopen('http://example.com', timeout=2)\"")
    # Network is disabled, it will fail to resolve.
    res_e = check(req, False, 1, False) 
    
    print("\nALL PASSED SUCCESSFULLY")
except AssertionError as e:
    print("ASSERTION FAILED:", e)
    sys.exit(1)
