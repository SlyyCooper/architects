from tangents.core.tool_validation import ToolValidator
from rich.console import Console

console = Console()

def test_valid_tool():
    """Test a valid tool configuration."""
    config = {
        "name": "calculator",
        "description": "A tool to perform basic calculations.",
        "handler": "math_tools.calculate",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to evaluate"
                }
            },
            "required": ["expression"]
        }
    }
    
    validator = ToolValidator()
    result = validator.validate_tool_config(config)
    
    console.print("\n=== Testing Valid Tool ===")
    console.print(validator.format_validation_result(result))

def test_invalid_tool():
    """Test an invalid tool configuration."""
    config = {
        "name": "bad tool!",  # Invalid name
        "description": "x",   # Too short
        "handler": "badpath", # Invalid handler path
        "input_schema": {     # Missing type
            "properties": {
                "param1": {
                    "type": "invalid_type"
                }
            }
        }
    }
    
    validator = ToolValidator()
    result = validator.validate_tool_config(config)
    
    console.print("\n=== Testing Invalid Tool ===")
    console.print(validator.format_validation_result(result))

def test_implementation_validation():
    """Test validating a tool's implementation."""
    def calculator(expression: str) -> str:
        """Calculate the result of a mathematical expression."""
        return str(eval(expression))
    
    schema = {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Mathematical expression to evaluate"
            }
        },
        "required": ["expression"]
    }
    
    validator = ToolValidator()
    result = validator.validate_tool_implementation(calculator, schema)
    
    console.print("\n=== Testing Implementation Validation ===")
    console.print(validator.format_validation_result(result))

def test_input_validation():
    """Test validating input values."""
    schema = {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "minLength": 2
            },
            "age": {
                "type": "integer",
                "minimum": 0
            }
        },
        "required": ["name", "age"]
    }
    
    # Test valid input
    valid_input = {
        "name": "Alice",
        "age": 25
    }
    
    # Test invalid input
    invalid_input = {
        "name": "A",  # Too short
        "age": -1    # Negative age
    }
    
    validator = ToolValidator()
    
    console.print("\n=== Testing Input Validation ===")
    console.print("\nValid Input:")
    result = validator.validate_input_values(valid_input, schema)
    console.print(validator.format_validation_result(result))
    
    console.print("\nInvalid Input:")
    result = validator.validate_input_values(invalid_input, schema)
    console.print(validator.format_validation_result(result))

def test_type_compatibility():
    """Test Python type hint compatibility with JSON schema."""
    def typed_function(
        str_param: str,
        int_param: int,
        float_param: float,
        bool_param: bool,
        list_param: list,
        dict_param: dict
    ) -> str:
        """A function with various type hints."""
        return "OK"
    
    schema = {
        "type": "object",
        "properties": {
            "str_param": {"type": "number"},     # Mismatched type
            "int_param": {"type": "integer"},    # Correct
            "float_param": {"type": "string"},   # Mismatched type
            "bool_param": {"type": "boolean"},   # Correct
            "list_param": {"type": "array"},     # Correct
            "dict_param": {"type": "string"}     # Mismatched type
        }
    }
    
    validator = ToolValidator()
    result = validator.validate_tool_implementation(typed_function, schema)
    
    console.print("\n=== Testing Type Compatibility ===")
    console.print(validator.format_validation_result(result))

def main():
    """Run all validation tests."""
    tests = [
        test_valid_tool,
        test_invalid_tool,
        test_implementation_validation,
        test_input_validation,
        test_type_compatibility
    ]
    
    for test in tests:
        test()
        print("\n" + "="*50)

if __name__ == "__main__":
    main() 