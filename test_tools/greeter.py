
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
