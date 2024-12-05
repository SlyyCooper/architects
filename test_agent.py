import os
from tangents.core.agent import Agent

def test_agent():
    # Initialize agent with a simple system prompt
    agent = Agent(
        name="TestBot",
        system_prompt="You are a helpful assistant. Keep responses short and concise.",
    )
    
    # Test with streaming enabled (default)
    print("\n=== Testing with streaming enabled ===")
    response = agent.think("Tell me a short joke about programming.")
    print("\nFull response:", response)
    
    # Test with streaming disabled
    print("\n=== Testing with streaming disabled ===")
    agent.stream = False
    response = agent.think("What is 2+2? Answer in one word.")
    print("\nFull response:", response)
    
    # Test memory functions
    print("\n=== Testing memory functions ===")
    agent.remember("favorite_number", 42)
    recalled_value = agent.recall("favorite_number")
    print(f"\nRecalled value matches: {recalled_value == 42}")

if __name__ == "__main__":
    test_agent() 