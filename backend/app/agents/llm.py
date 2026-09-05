"""LLM Provider abstraction and mock implementation."""

from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    """Abstract interface for LLM operations inside the Agent workflow."""

    @abstractmethod
    def generate(self, prompt: str, system: str = "") -> str:
        """Generate text based on a prompt and optional system instructions."""
        pass


class MockLLMProvider(BaseLLMProvider):
    """Deterministic LLM for testing isolated LangGraph nodes without APIs."""
    
    def __init__(self):
        self.call_count = 0
        
    def generate(self, prompt: str, system: str = "") -> str:
        self.call_count += 1
        
        system_lower = system.lower()
        prompt_lower = prompt.lower()
        
        if "coder" in system_lower:
            return (
                "Proposed changes:\n"
                "- Modify `foo.py` to add `bar()`\n"
                "- Ensure backwards compatibility."
            )
        elif "planner" in system_lower or "plan" in prompt_lower:
            return "1. Inspect repository\n2. Locate relevant files\n3. Propose required change"
            
        return "Deterministic default specific to the Mock LLM."
