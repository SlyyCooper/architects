from tangents.core.tool_validation import (
    ToolValidator, ValidationRule, ValidationLevel, ValidationProfile
)
from rich.console import Console

console = Console()

def test_custom_rules():
    """Test adding and using custom validation rules."""
    print("\n=== Testing Custom Rules ===")
    
    # Create validator with custom rules
    validator = ToolValidator()
    
    # Add custom rules
    validator.create_rule(
        name="keyword_in_description",
        check_func=lambda desc: (
            "Description should mention 'API' for API tools" 
            if "api" not in desc.lower() else None
        ),
        level=ValidationLevel.WARNING,
        description="Check for API keyword in description",
        category="description"
    )
    
    validator.create_rule(
        name="secure_handler",
        check_func=lambda handler: (
            "Handler should use HTTPS for web endpoints" 
            if handler.startswith("http://") else None
        ),
        level=ValidationLevel.ERROR,
        description="Check for secure handler endpoints",
        category="handler"
    )
    
    # Test with custom rules
    config = {
        "name": "web_tool",
        "description": "A tool to fetch web content",  # Missing API keyword
        "handler": "http://api.example.com",  # Insecure handler
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string"}
            }
        }
    }
    
    result = validator.validate_tool_config(config)
    console.print(validator.format_validation_result(result))

def test_validation_profiles():
    """Test different validation profiles."""
    print("\n=== Testing Validation Profiles ===")
    
    config = {
        "name": "my_tool",
        "description": "x",  # Short description (warning)
        "handler": "module.function",
        "input_schema": {
            "type": "object",
            "properties": {
                "param": {
                    "type": "string"
                }
            }
        }
    }
    
    # Test with different profiles
    profiles = [
        ValidationProfile.STRICT,
        ValidationProfile.STANDARD,
        ValidationProfile.LENIENT
    ]
    
    for profile in profiles:
        console.print(f"\n[bold]{profile.value.title()} Profile:[/bold]")
        validator = ToolValidator(profile=profile)
        result = validator.validate_tool_config(config)
        console.print(validator.format_validation_result(result))

def test_rule_management():
    """Test enabling/disabling rules."""
    print("\n=== Testing Rule Management ===")
    
    validator = ToolValidator()
    
    # Disable some rules
    validator.disable_rule("description_length")
    validator.disable_rule("description_punctuation")
    
    config = {
        "name": "my_tool",
        "description": "x",  # Should not trigger disabled rules
        "handler": "module.function",
        "input_schema": {
            "type": "object",
            "properties": {
                "param": {"type": "string"}
            }
        }
    }
    
    console.print("\nWith disabled rules:")
    result = validator.validate_tool_config(config)
    console.print(validator.format_validation_result(result))
    
    # Re-enable rules
    validator.enable_rule("description_length")
    validator.enable_rule("description_punctuation")
    
    console.print("\nWith re-enabled rules:")
    result = validator.validate_tool_config(config)
    console.print(validator.format_validation_result(result))

def test_dynamic_rule_creation():
    """Test creating rules dynamically."""
    print("\n=== Testing Dynamic Rule Creation ===")
    
    validator = ToolValidator()
    
    # Create rules based on conditions
    min_desc_length = 20
    required_keywords = ["async", "await"]
    
    validator.create_rule(
        name="min_description_length",
        check_func=lambda desc: (
            f"Description should be at least {min_desc_length} chars" 
            if len(desc) < min_desc_length else None
        ),
        level=ValidationLevel.WARNING
    )
    
    validator.create_rule(
        name="async_keywords",
        check_func=lambda desc: (
            f"Async tool should mention {required_keywords}" 
            if not any(k in desc.lower() for k in required_keywords) else None
        ),
        level=ValidationLevel.SUGGESTION
    )
    
    config = {
        "name": "async_tool",
        "description": "A simple tool",  # Too short, missing keywords
        "handler": "module.function",
        "input_schema": {"type": "object"}
    }
    
    result = validator.validate_tool_config(config)
    console.print(validator.format_validation_result(result))

def main():
    """Run all validation feature tests."""
    tests = [
        test_custom_rules,
        test_validation_profiles,
        test_rule_management,
        test_dynamic_rule_creation
    ]
    
    for test in tests:
        test()
        print("\n" + "="*50)

if __name__ == "__main__":
    main() 