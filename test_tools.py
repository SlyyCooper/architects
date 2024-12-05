from tangents.core.agent import Agent
from tangents.core.tool_types import Tool, ToolConfig

def get_weather(location: str) -> str:
    """Simple mock weather function."""
    return f"The weather in {location} is sunny and 72°F"

def main():
    # Create an agent
    agent = Agent(
        name="WeatherBot",
        system_prompt="You are a helpful weather assistant. Use the weather tool when asked about weather."
    )
    
    # Create a weather tool
    weather_tool = Tool(
        name="get_weather",
        description="""Get the current weather in a given location.
        Use this tool when users ask about weather conditions in a specific place.
        The tool returns temperature and conditions.""",
        input_schema={
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA"
                }
            },
            "required": ["location"]
        },
        handler=get_weather
    )
    
    # Add the tool to the agent
    agent.add_tool(weather_tool)
    
    # Configure tool usage (optional - defaults are usually fine)
    agent.configure_tools(ToolConfig(
        type="auto",  # Let Claude decide when to use tools
        disable_parallel_tool_use=True  # Use one tool at a time
    ))
    
    # Test the agent with different queries
    queries = [
        "What's the weather like in San Francisco?",
        "Tell me about the weather in New York City.",
        "How are you today?"  # Non-weather query to show tool isn't always used
    ]
    
    for query in queries:
        print(f"\n=== Query: {query} ===")
        response = agent.think(query)
        print("\nFinal response:", response)

if __name__ == "__main__":
    main() 