from tangents.core.tool_loader import DynamicToolSystem

@DynamicToolSystem.register(
    name="search",
    description="Description of the tool",
    input_schema={
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "Parameter description"
            }
        },
        "required": ["param1"]
    }
)
def search_handler(param1: str):
    """Tool implementation."""
    pass
