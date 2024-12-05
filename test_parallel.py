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

def slow_square(a: int) -> str:
    """A deliberately slow square function."""
    time.sleep(2)  # Simulate slow operation
    return f"{a}² = {a * a}"

def main():
    # Create an agent with math capabilities
    agent = Agent(
        name="MathBot",
        system_prompt="""You are a math assistant. Use the available tools to perform calculations.
        When given multiple calculations, try to do them in parallel when possible."""
    )
    
    # Add math tools
    tools = [
        Tool(
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
        ),
        Tool(
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
        ),
        Tool(
            name="slow_square",
            description="Square a number (takes 2 seconds)",
            input_schema={
                "type": "object",
                "properties": {
                    "a": {"type": "integer"}
                },
                "required": ["a"]
            },
            handler=slow_square
        )
    ]
    
    for tool in tools:
        agent.add_tool(tool)
    
    # Complex calculation that benefits from parallelization
    complex_task = """Calculate all of these and show your work:
    1. 2 + 3
    2. 4 * 5
    3. 6²
    Explain each step and give the final results."""
    
    # Test with parallel execution enabled (default)
    print("\n=== Testing with parallel execution ENABLED ===")
    start_time = time.time()
    result = agent.think(complex_task)
    end_time = time.time()
    print(f"\nTime taken with parallel execution: {end_time - start_time:.2f} seconds")
    
    # Test with parallel execution disabled
    print("\n=== Testing with parallel execution DISABLED ===")
    agent.set_parallel_execution(False)
    start_time = time.time()
    result = agent.think(complex_task)
    end_time = time.time()
    print(f"\nTime taken without parallel execution: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main() 