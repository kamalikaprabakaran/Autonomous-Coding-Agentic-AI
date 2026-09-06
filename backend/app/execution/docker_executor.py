"""Docker Sandboxed Executor logic."""

import docker
import os
from typing import Optional
from backend.app.models.execution import ExecutionRequest, ExecutionResult
from backend.app.core.config import get_settings
from backend.app.services.analyzer.discovery import resolve_safe_path

class DockerExecutor:
    """Manages secure sandbox execution via local Docker."""
    
    def __init__(self):
        self.settings = get_settings()
        try:
            self.client = docker.from_env()
        except Exception:
            self.client = None
            
    def execute(self, req: ExecutionRequest) -> ExecutionResult:
        """Executes a command safely inside an isolated container."""
        import time
        from requests.exceptions import ReadTimeout
        # 1. Dependency validation
        if not self.client:
            return ExecutionResult(
                success=False,
                error="Docker engine is unavailable on host."
            )
            
        # 2. Config/Limits resolution
        image = self.settings.SANDBOX_IMAGE
        timeout = req.timeout_seconds or self.settings.SANDBOX_TIMEOUT_SECONDS
        mem_limit = req.memory_limit or self.settings.SANDBOX_MEMORY_LIMIT
        cpu_limit = req.cpu_limit or self.settings.SANDBOX_CPU_LIMIT
        net_enabled = req.network_enabled if req.network_enabled is not None else self.settings.SANDBOX_NETWORK_ENABLED
        
        # 3. Path boundaries
        try:
            # Resolving relative to itself enforces absolute boundaries accurately
            repo_path = resolve_safe_path(req.repository_path, ".")
        except ValueError as e:
            return ExecutionResult(success=False, error=f"Repository boundary violation: {str(e)}")
        except FileNotFoundError as e:
            return ExecutionResult(success=False, error="Repository path does not exist.")
            
        if not repo_path.is_dir():
            return ExecutionResult(
                success=False,
                error="Repository path does not exist."
            )
            
        repo_host_str = str(repo_path.absolute())
        bindings = {repo_host_str: {'bind': '/sandbox/repo', 'mode': 'ro'}}
        
        # Nano_cpus math: CPU_limit 1.0 -> 1_000_000_000
        nano_cpus = int(cpu_limit * 1_000_000_000)
        
        container = None
        duration = 0.0
        start_time = time.monotonic()
        
        try:
            # 4. Container spawn securely
            container = self.client.containers.run(
                image=image,
                command=req.command,
                detach=True,
                working_dir='/sandbox/repo',
                volumes=bindings,
                mem_limit=mem_limit,
                nano_cpus=nano_cpus,
                network_mode="bridge" if net_enabled else "none",
                privileged=False,
                cap_drop=["ALL"], 
                user="sandboxuser:sandboxuser"
            )
            
            # Wait for execution respecting explicit timeouts
            try:
                wait_result = container.wait(timeout=timeout)
                exit_code = wait_result.get('StatusCode', -1)
                duration = time.monotonic() - start_time
                
                # Extract logs seamlessly (stdout vs stderr)
                logs_out = container.logs(stdout=True, stderr=False).decode('utf-8', errors='replace')
                logs_err = container.logs(stdout=False, stderr=True).decode('utf-8', errors='replace')
                
                return ExecutionResult(
                    success=(exit_code == 0),
                    exit_code=exit_code,
                    stdout=logs_out,
                    stderr=logs_err,
                    timed_out=False,
                    duration_seconds=duration
                )
            except (docker.errors.APIError, ReadTimeout) as e:
                err_msg = str(e)
                if "Read timed out" in err_msg or "timeout" in err_msg.lower():
                    duration = time.monotonic() - start_time
                    try:
                        container.stop(timeout=1)
                    except Exception:
                        try:
                            container.kill()
                        except Exception:
                            pass
                            
                    logs_out = ""
                    logs_err = ""
                    try:
                        logs_out = container.logs(stdout=True, stderr=False).decode('utf-8', errors='replace')
                        logs_err = container.logs(stdout=False, stderr=True).decode('utf-8', errors='replace')
                    except Exception:
                        pass
                        
                    return ExecutionResult(
                        success=False,
                        timed_out=True,
                        error="Execution timeout reached.",
                        stdout=logs_out,
                        stderr=logs_err,
                        duration_seconds=duration,
                        exit_code=-1
                    )
                raise  # re-raise if it's not a timeout
            
        except docker.errors.ImageNotFound:
            duration = time.monotonic() - start_time
            return ExecutionResult(success=False, error=f"Sandbox image {image} missing.", duration_seconds=duration)
        except Exception as e:
            duration = time.monotonic() - start_time
            err_msg = str(e)
            
            # Additional fallback logic just in case an exception string matches "timeout"
            if "Read timed out" in err_msg or "timeout" in err_msg.lower():
                return ExecutionResult(
                    success=False,
                    timed_out=True,
                    error="Execution timeout reached.",
                    duration_seconds=duration
                )
            
            return ExecutionResult(success=False, error=err_msg, duration_seconds=duration)
            
        finally:
            # 5. Guaranteed manual cleanup since container shouldn't linger
            if container:
                try:
                    container.remove(force=True)
                except Exception:
                    pass
