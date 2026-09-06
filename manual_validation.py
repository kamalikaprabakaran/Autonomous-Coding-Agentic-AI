import sys
from backend.app.agents.graph import run_agent
from backend.app.agents.llm import MockLLMProvider
from backend.app.services.analyzer.analyzer import RepositoryAnalyzer
from backend.app.tools.registry import ToolRegistry
import pprint

analyzer = RepositoryAnalyzer()
tools = ToolRegistry()

def print_report(scenario_name, final_state):
    print(f"\n{'='*50}\nSCENARIO: {scenario_name}\n{'='*50}")
    print(f"Final Status: {final_state.get('final_status')}")
    print(f"Iteration Count: {final_state.get('iteration_count')}")
    print(f"Execution Result:\n  {final_state.get('execution_result')}")
    print(f"Evaluation Result:\n  {final_state.get('evaluation_result')}")
    print(f"Failure Feedback:\n  {final_state.get('failure_feedback')}")
    print("Correction History:")
    for c in final_state.get("correction_history", []):
         print(f"  Attempt {c.get('iteration')}: Success? {c['evaluation_result']['passed']}")
    print(f"\nLength of messages: {len(final_state.get('messages', []))}")

# 1. SUCCESS ON FIRST ATTEMPT
print("\n--- Running Scenario 1---")
llm = MockLLMProvider()
state = run_agent("Simple valid task", ".", llm, analyzer, tools)
print_report("1. SUCCESS ON FIRST ATTEMPT", state)

# 2. FAILURE THEN CORRECTION
print("\n--- Running Scenario 2---")
class FailingMockLLM(MockLLMProvider):
    def generate(self, prompt: str, system: str = "") -> str:
        if "Previous attempt failed" in prompt:
            return "Corrected proposed changes:\n- Passed tests successfully."
        if "coder" in system.lower():
            return "bad proposal"
        return super().generate(prompt, system)

state2 = run_agent("Make it fail", ".", FailingMockLLM(), analyzer, tools)
print_report("2. FAILURE THEN CORRECTION", state2)

# 3. MAXIMUM ITERATIONS
print("\n--- Running Scenario 3---")
class StubbornFailingLLM(MockLLMProvider):
    def generate(self, prompt: str, system: str = "") -> str:
        if "coder" in system.lower():
            return "bad proposal"
        return super().generate(prompt, system)

state3 = run_agent("Always fail", ".", StubbornFailingLLM(), analyzer, tools, max_iterations=3)
print_report("3. MAXIMUM ITERATIONS (LIMIT 3)", state3)

# 4. EXECUTOR FAILURE
print("\n--- Running Scenario 4---")
class ThrowingExecutor:
    def execute(self, req):
        raise Exception("Docker execution completely crashed")
            
state4 = run_agent("Crash executor", ".", MockLLMProvider(), analyzer, tools, executor=ThrowingExecutor())
print_report("4. EXECUTOR FAILURE", state4)
