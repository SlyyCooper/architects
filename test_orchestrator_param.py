from tangents.core.agent import Agent

def main():
    # Create a regular agent
    regular_agent = Agent(
        name="RegularBot",
        system_prompt="You are a helpful assistant.",
        is_orchestrator=False  # This is the default
    )
    
    # Create an orchestrator agent
    orchestrator = Agent(
        name="OrchestratorBot",
        system_prompt="You are a helpful assistant.",
        is_orchestrator=True  # Enable orchestrator capabilities
    )
    
    # Try to use orchestration features with both agents
    print("\n=== Testing Regular Agent ===")
    result = regular_agent.orchestrate("Write a blog post")
    print("Regular Agent Result:", result)
    
    print("\n=== Testing Orchestrator Agent ===")
    
    # Register some specialized agents with the orchestrator
    agents_to_register = [
        {
            "agent_name": "ResearchAgent",
            "description": "Specialized in research and fact-checking",
            "capabilities": ["research", "fact-checking"],
            "system_prompt": "You are a research specialist."
        },
        {
            "agent_name": "WriterAgent",
            "description": "Specialized in writing and editing",
            "capabilities": ["writing", "editing"],
            "system_prompt": "You are a writing specialist."
        }
    ]
    
    print("\nRegistering specialized agents:")
    for agent_info in agents_to_register:
        result = orchestrator._handle_register_agent(**agent_info)
        print(result)
    
    print("\nChecking agent status:")
    print(orchestrator._handle_check_status())
    
    print("\nTesting orchestration:")
    result = orchestrator.orchestrate("""
    Create a blog post about AI:
    1. Research recent AI developments
    2. Write an engaging article
    """)
    print("\nOrchestrator Result:", result)

if __name__ == "__main__":
    main() 