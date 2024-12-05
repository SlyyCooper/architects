from tangents.core.tool_loader import DynamicToolSystem
import os
from pathlib import Path

def setup_test_tools():
    """Create test tool files."""
    # Create test tools directory
    tools_dir = Path("test_tools")
    tools_dir.mkdir(exist_ok=True)
    
    # Create a YAML-based tool
    yaml_tool = """
name: calculator
description: Perform basic calculations
handler: test_tool_loader.calculate
input_schema:
  type: object
  properties:
    expression:
      type: string
      description: Mathematical expression to evaluate
  required: [expression]
"""
    with open(tools_dir / "calculator.yaml", "w") as f:
        f.write(yaml_tool)
    
    # Create a Python-based tool using decorator
    py_tool = """
from tangents.core.tool_loader import DynamicToolSystem

@DynamicToolSystem.register(
    name="greeter",
    description="Generate a greeting message",
    input_schema={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Name to greet"
            },
            "language": {
                "type": "string",
                "description": "Language for greeting",
                "default": "English"
            }
        },
        "required": ["name"]
    }
)
def greet(name: str, language: str = "English") -> str:
    greetings = {
        "English": "Hello",
        "Spanish": "Hola",
        "French": "Bonjour"
    }
    greeting = greetings.get(language, "Hello")
    return f"{greeting}, {name}!"
"""
    with open(tools_dir / "greeter.py", "w") as f:
        f.write(py_tool)

def calculate(expression: str) -> str:
    """Handler for calculator tool."""
    try:
        result = eval(expression, {"__builtins__": {}})
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    # Set up test tools
    setup_test_tools()
    
    print("\n=== Testing Dynamic Tool System ===")
    
    # Initialize tool system
    tool_system = DynamicToolSystem(tools_dir="test_tools")
    
    # List available tools
    print("\nAvailable tools:", tool_system.list_tools())
    
    # Test calculator tool
    print("\n=== Testing Calculator Tool ===")
    calc_tool = tool_system.get_tool("calculator")
    result = calc_tool.handler("2 + 2")
    print("Calculation:", result)
    
    # Test greeter tool
    print("\n=== Testing Greeter Tool ===")
    greet_tool = tool_system.get_tool("greeter")
    result = greet_tool.handler(name="Alice", language="Spanish")
    print("Greeting:", result)
    
    # Create a new tool template
    print("\n=== Creating New Tool Template ===")
    try:
        tool_system.create_tool_template("search", template_type="python")
    except FileExistsError:
        print("Tool template already exists")
    
    # Test tool reloading
    print("\n=== Testing Tool Reload ===")
    tool_system.reload_tools()
    print("Tools after reload:", tool_system.list_tools())
    
    # Clean up test files
    print("\n=== Cleaning Up ===")
    for file in Path("test_tools").glob("*"):
        file.unlink()
    Path("test_tools").rmdir()
    print("Test files cleaned up")

if __name__ == "__main__":
    main() 