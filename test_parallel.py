from tangents.core.agent import Agent
from tangents.core.tool_types import Tool
import time

def slow_add(a: int, b: int) -> str:
    """A deliberately slow addition function."""
    time.sleep(2)  # Simulate slow operation
    return f"{a} + {b} = {a + b}"

def slow_multiply(a: int, b: int) -> str:
    """A deliberately slow multiplication function."""
    time.sleep(2)  # Simulate slow operation
    return f"{a} * {b} = {a * b}"

def main():
    # Create an agent with math capabilities
    agent = Agent(
        name="MathBot",
        system_prompt="You are a math assistant. Use the available tools to perform calculations."
    )
    
    # Add math tools
    add_tool = Tool(
        name="slow_add",
        description="Add two numbers (takes 2 seconds)",
        input_schema={
            "type": "object",
            "properties": {
                "a": {"type": "integer"},
                "b": {"type": "integer"}
            },
            "required": ["a", "b"]
        },
        handler=slow_add
    )
    
    multiply_tool = Tool(
        name="slow_multiply",
        description="Multiply two numbers (takes 2 seconds)",
        input_schema={
            "type": "object",
            "properties": {
                "a": {"type": "integer"},
                "b": {"type": "integer"}
            },
            "required": ["a", "b"]
        },
        handler=slow_multiply
    )
    
    agent.add_tool(add_tool)
    agent.add_tool(multiply_tool)
    
    # Test with parallel execution enabled (default)
    print("\n=== Testing with parallel execution ENABLED ===")
    start_time = time.time()
    result = agent.think("Calculate (2 + 3) and (4 * 5) and show your work.")
    end_time = time.time()
    print(f"\nTime taken with parallel execution: {end_time - start_time:.2f} seconds")
    
    # Test with parallel execution disabled
    print("\n=== Testing with parallel execution DISABLED ===")
    agent.set_parallel_execution(False)
    start_time = time.time()
    result = agent.think("Calculate (2 + 3) and (4 * 5) and show your work.")
    end_time = time.time()
    print(f"\nTime taken without parallel execution: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main() 