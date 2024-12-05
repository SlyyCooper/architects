from tangents.core.agent import Agent
from tangents.cli.interface import display_logo
from rich.console import Console
from rich.panel import Panel

console = Console()

def main():
    # Display the cool logo
    display_logo()
    
    # Create a streaming agent (default)
    streaming_agent = Agent(
        name="T.A.N.gent (Streaming)",
        system_prompt="You are a helpful AI assistant that specializes in Python programming. You provide clear, concise explanations with code examples.",
        stream=True  # Enable streaming (default)
    )
    
    # Create a non-streaming agent
    non_streaming_agent = Agent(
        name="T.A.N.gent (Non-Streaming)",
        system_prompt="You are a helpful AI assistant that specializes in Python programming. You provide clear, concise explanations with code examples.",
        stream=False  # Disable streaming
    )
    
    # Test prompt
    prompt = """Write a simple hello world function in Python."""
    
    # Demonstrate streaming response
    console.print(Panel("Testing Streaming Response", style="bold magenta"))
    streaming_agent.think(prompt)
    
    # Add some spacing
    console.print("\n" * 2)
    
    # Demonstrate non-streaming response
    console.print(Panel("Testing Non-Streaming Response", style="bold magenta"))
    non_streaming_agent.think(prompt)

if __name__ == "__main__":
    main() 