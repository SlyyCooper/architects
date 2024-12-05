from typing import Dict, Any, List, Optional, Set, Union, Callable, Type
from dataclasses import dataclass, field
from enum import Enum
import jsonschema
import inspect
from pathlib import Path
import yaml
from rich.console import Console
from rich.panel import Panel

console = Console()

class ValidationLevel(Enum):
    """Validation levels for rules."""
    ERROR = "error"
    WARNING = "warning"
    SUGGESTION = "suggestion"

class ValidationProfile(Enum):
    """Predefined validation profiles."""
    STRICT = "strict"      # All rules enabled, treat warnings as errors
    STANDARD = "standard"  # All rules enabled, normal behavior
    LENIENT = "lenient"   # Only critical rules enabled
    CUSTOM = "custom"     # Custom rule configuration

@dataclass
class ValidationRule:
    """Defines a validation rule."""
    name: str
    description: str
    level: ValidationLevel
    check_func: Callable[..., Optional[str]]
    enabled: bool = True
    category: str = "general"
    
    def apply(self, *args, **kwargs) -> Optional[str]:
        """Apply the rule if enabled."""
        if self.enabled:
            return self.check_func(*args, **kwargs)
        return None

@dataclass
class ValidationResult:
    """Result of a tool validation check."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    applied_rules: List[str] = field(default_factory=list)

class ToolValidator:
    """Comprehensive tool validation system with custom rules and profiles."""
    
    # Standard JSON schema types
    VALID_TYPES = {"string", "number", "integer", "boolean", "array", "object", "null"}
    
    # Required fields for tool configuration
    REQUIRED_TOOL_FIELDS = {
        "name": str,
        "description": str,
        "handler": str,
        "input_schema": dict
    }
    
    def __init__(self, profile: ValidationProfile = ValidationProfile.STANDARD):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.suggestions: List[str] = []
        self.applied_rules: List[str] = []
        self.profile = profile
        self.custom_rules: Dict[str, ValidationRule] = {}
        
        # Initialize default rules
        self._setup_default_rules()
        
        # Apply profile configuration
        self._apply_profile(profile)
    
    def _setup_default_rules(self):
        """Set up default validation rules."""
        # Name rules
        self.add_rule(ValidationRule(
            name="valid_name_format",
            description="Tool name must be a valid identifier",
            level=ValidationLevel.ERROR,
            check_func=lambda name: (
                "Tool name must be a valid Python identifier" 
                if not name.isidentifier() else None
            ),
            category="name"
        ))
        
        self.add_rule(ValidationRule(
            name="name_length",
            description="Check name length",
            level=ValidationLevel.WARNING,
            check_func=lambda name: (
                "Tool name is quite long (>64 chars)" 
                if len(name) > 64 else None
            ),
            category="name"
        ))
        
        # Description rules
        self.add_rule(ValidationRule(
            name="description_length",
            description="Check description length",
            level=ValidationLevel.WARNING,
            check_func=lambda desc: (
                "Description is too short (<10 chars)" 
                if len(desc) < 10 else None
            ),
            category="description"
        ))
        
        self.add_rule(ValidationRule(
            name="description_punctuation",
            description="Check description punctuation",
            level=ValidationLevel.SUGGESTION,
            check_func=lambda desc: (
                "Description should end with punctuation" 
                if not desc.endswith((".", "!", "?")) else None
            ),
            category="description"
        ))
    
    def add_rule(self, rule: ValidationRule) -> None:
        """Add a custom validation rule."""
        self.custom_rules[rule.name] = rule
        console.print(f"[blue]Added validation rule:[/blue] {rule.name}")
    
    def remove_rule(self, rule_name: str) -> None:
        """Remove a validation rule."""
        if rule_name in self.custom_rules:
            del self.custom_rules[rule_name]
            console.print(f"[yellow]Removed validation rule:[/yellow] {rule_name}")
    
    def enable_rule(self, rule_name: str) -> None:
        """Enable a validation rule."""
        if rule_name in self.custom_rules:
            self.custom_rules[rule_name].enabled = True
    
    def disable_rule(self, rule_name: str) -> None:
        """Disable a validation rule."""
        if rule_name in self.custom_rules:
            self.custom_rules[rule_name].enabled = False
    
    def _apply_profile(self, profile: ValidationProfile) -> None:
        """Apply a validation profile configuration."""
        if profile == ValidationProfile.STRICT:
            # Enable all rules and treat warnings as errors
            for rule in self.custom_rules.values():
                rule.enabled = True
                if rule.level == ValidationLevel.WARNING:
                    rule.level = ValidationLevel.ERROR
        
        elif profile == ValidationProfile.STANDARD:
            # Enable all rules with default levels
            for rule in self.custom_rules.values():
                rule.enabled = True
        
        elif profile == ValidationProfile.LENIENT:
            # Only enable error-level rules
            for rule in self.custom_rules.values():
                rule.enabled = (rule.level == ValidationLevel.ERROR)
    
    def set_profile(self, profile: ValidationProfile) -> None:
        """Change the validation profile."""
        self.profile = profile
        self._apply_profile(profile)
        console.print(f"[blue]Set validation profile:[/blue] {profile.value}")
    
    def validate_tool_config(self, config: Dict[str, Any]) -> ValidationResult:
        """Validate a complete tool configuration."""
        self.errors = []
        self.warnings = []
        self.suggestions = []
        self.applied_rules = []
        
        # Apply relevant rules for each component
        if "name" in config:
            self._apply_rules_by_category("name", config["name"])
        
        if "description" in config:
            self._apply_rules_by_category("description", config["description"])
        
        # Continue with other validations...
        self._validate_required_fields(config)
        if "input_schema" in config:
            self._validate_input_schema(config["input_schema"])
        if "handler" in config:
            self._validate_handler_path(config["handler"])
        
        return self._get_result()
    
    def _apply_rules_by_category(self, category: str, value: Any) -> None:
        """Apply all enabled rules for a specific category."""
        for rule in self.custom_rules.values():
            if rule.category == category and rule.enabled:
                if result := rule.apply(value):
                    self.applied_rules.append(rule.name)
                    if rule.level == ValidationLevel.ERROR:
                        self.errors.append(result)
                    elif rule.level == ValidationLevel.WARNING:
                        self.warnings.append(result)
                    else:
                        self.suggestions.append(result)
    
    def create_rule(self, name: str, check_func: Callable, 
                   level: ValidationLevel = ValidationLevel.WARNING,
                   description: str = "", category: str = "custom") -> None:
        """Create and add a new validation rule."""
        rule = ValidationRule(
            name=name,
            description=description or f"Custom rule: {name}",
            level=level,
            check_func=check_func,
            category=category
        )
        self.add_rule(rule)
    
    def validate_tool_implementation(self, handler: Any, 
                                   input_schema: Dict[str, Any]) -> ValidationResult:
        """Validate a tool's implementation against its schema."""
        self.errors = []
        self.warnings = []
        self.suggestions = []
        
        if not callable(handler):
            self.errors.append("Handler must be a callable function")
            return self._get_result()
        
        # Get function signature
        sig = inspect.signature(handler)
        params = sig.parameters
        
        # Check parameters against schema
        self._validate_parameters_against_schema(params, input_schema)
        
        # Check return type hint
        self._validate_return_type(sig)
        
        # Check docstring
        self._validate_docstring(handler)
        
        return self._get_result()
    
    def validate_input_values(self, values: Dict[str, Any], 
                            schema: Dict[str, Any]) -> ValidationResult:
        """Validate input values against the schema."""
        self.errors = []
        self.warnings = []
        self.suggestions = []
        
        try:
            jsonschema.validate(instance=values, schema=schema)
        except jsonschema.exceptions.ValidationError as e:
            self.errors.append(f"Input validation error: {str(e)}")
        except jsonschema.exceptions.SchemaError as e:
            self.errors.append(f"Schema error: {str(e)}")
        
        return self._get_result()
    
    def _validate_required_fields(self, config: Dict[str, Any]) -> None:
        """Validate that all required fields are present and of correct type."""
        for field, expected_type in self.REQUIRED_TOOL_FIELDS.items():
            if field not in config:
                self.errors.append(f"Missing required field: {field}")
            elif not isinstance(config[field], expected_type):
                self.errors.append(
                    f"Field '{field}' must be of type {expected_type.__name__}"
                )
    
    def _validate_name(self, name: str) -> None:
        """Validate tool name."""
        if not name:
            self.errors.append("Tool name cannot be empty")
        if not name.isidentifier():
            self.errors.append(
                "Tool name must be a valid Python identifier "
                "(letters, numbers, underscore, no spaces)"
            )
        if len(name) > 64:
            self.warnings.append(
                "Tool name is quite long. Consider using a shorter name "
                "for better readability"
            )
    
    def _validate_description(self, description: str) -> None:
        """Validate tool description."""
        if len(description) < 10:
            self.warnings.append(
                "Tool description is very short. Consider providing more detail"
            )
        if len(description) > 1000:
            self.warnings.append(
                "Tool description is very long. Consider making it more concise"
            )
        if not description.endswith((".", "!", "?")):
            self.suggestions.append(
                "Consider ending the description with proper punctuation"
            )
    
    def _validate_input_schema(self, schema: Dict[str, Any]) -> None:
        """Validate the input schema structure."""
        try:
            # Validate schema itself
            jsonschema.validators.validator_for(schema).check_schema(schema)
            
            # Additional checks
            if "type" not in schema:
                self.errors.append("Schema must specify a type")
            elif schema["type"] not in self.VALID_TYPES:
                self.errors.append(f"Invalid schema type: {schema['type']}")
            
            if "properties" in schema:
                for prop_name, prop_schema in schema["properties"].items():
                    if "description" not in prop_schema:
                        self.warnings.append(
                            f"Property '{prop_name}' is missing a description"
                        )
            
            if "required" in schema and not isinstance(schema["required"], list):
                self.errors.append("'required' must be a list of property names")
            
        except jsonschema.exceptions.SchemaError as e:
            self.errors.append(f"Invalid schema: {str(e)}")
    
    def _validate_handler_path(self, handler_path: str) -> None:
        """Validate the handler path format."""
        if not handler_path:
            self.errors.append("Handler path cannot be empty")
            return
        
        parts = handler_path.split(".")
        if len(parts) < 2:
            self.errors.append(
                "Handler path must be in format: module.function"
            )
        
        for part in parts:
            if not part.isidentifier():
                self.errors.append(
                    f"Invalid handler path component: {part}"
                )
    
    def _validate_parameters_against_schema(self, 
                                         params: Dict[str, inspect.Parameter],
                                         schema: Dict[str, Any]) -> None:
        """Validate function parameters against input schema."""
        if "properties" not in schema:
            self.warnings.append("Schema doesn't define any properties")
            return
        
        schema_props = schema.get("properties", {})
        required_props = schema.get("required", [])
        
        # Check each parameter has a corresponding schema property
        for param_name, param in params.items():
            if param_name not in schema_props:
                self.errors.append(
                    f"Parameter '{param_name}' not defined in schema"
                )
            else:
                # Check parameter type hint against schema
                param_type = param.annotation if param.annotation != inspect.Parameter.empty else Any
                schema_type = schema_props[param_name].get("type")
                self._validate_type_compatibility(param_name, param_type, schema_type)
        
        # Check each required schema property has a parameter
        for prop_name in required_props:
            if prop_name not in params:
                self.errors.append(
                    f"Required property '{prop_name}' missing from function parameters"
                )
    
    def _validate_return_type(self, sig: inspect.Signature) -> None:
        """Validate function return type hint."""
        return_annotation = sig.return_annotation
        if return_annotation == inspect.Signature.empty:
            self.warnings.append(
                "Function is missing a return type hint"
            )
    
    def _validate_docstring(self, handler: Any) -> None:
        """Validate function docstring."""
        if not handler.__doc__:
            self.warnings.append("Function is missing a docstring")
        elif len(handler.__doc__.strip()) < 10:
            self.warnings.append(
                "Function has a very short docstring. Consider adding more detail"
            )
    
    def _validate_type_compatibility(self, name: str, 
                                   python_type: Any, 
                                   schema_type: str) -> None:
        """Validate Python type compatibility with JSON schema type."""
        type_mapping = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object",
            None: "null"
        }
        
        if python_type in type_mapping:
            expected_schema_type = type_mapping[python_type]
            if schema_type != expected_schema_type:
                self.warnings.append(
                    f"Parameter '{name}' type hint ({python_type.__name__}) "
                    f"doesn't match schema type ({schema_type})"
                )
    
    def _get_result(self) -> ValidationResult:
        """Create a ValidationResult from current state."""
        is_valid = len(self.errors) == 0
        if self.profile == ValidationProfile.STRICT:
            is_valid = len(self.errors) == 0 and len(self.warnings) == 0
            
        return ValidationResult(
            is_valid=is_valid,
            errors=self.errors.copy(),
            warnings=self.warnings.copy(),
            suggestions=self.suggestions.copy(),
            applied_rules=self.applied_rules.copy()
        )
    
    @staticmethod
    def format_validation_result(result: ValidationResult) -> str:
        """Format validation result for display."""
        status = "[green]VALID[/green]" if result.is_valid else "[red]INVALID[/red]"
        
        sections = [
            ("Errors", result.errors, "red"),
            ("Warnings", result.warnings, "yellow"),
            ("Suggestions", result.suggestions, "blue"),
            ("Applied Rules", result.applied_rules, "cyan")
        ]
        
        output = [f"Validation Status: {status}"]
        
        for title, items, color in sections:
            if items:
                output.append(f"\n[{color}]{title}:[/{color}]")
                for item in items:
                    output.append(f"  • {item}")
        
        return "\n".join(output) 