from tangents.agents.orchestrator import OrchestratorAgent

def main():
    # Create the orchestrator agent
    orchestrator = OrchestratorAgent()
    
    # Register some specialized agents
    research_agent = {
        "agent_name": "ResearchAgent",
        "description": "Specialized in gathering and analyzing information from various sources",
        "capabilities": ["web research", "data analysis", "fact checking"],
        "system_prompt": "You are a research specialist focused on gathering accurate information and analyzing data."
    }
    
    writer_agent = {
        "agent_name": "WriterAgent",
        "description": "Expert in creating well-written, engaging content",
        "capabilities": ["content writing", "editing", "summarization"],
        "system_prompt": "You are a skilled writer focused on creating clear, engaging, and well-structured content."
    }
    
    code_agent = {
        "agent_name": "CodeAgent",
        "description": "Specialized in writing and reviewing code",
        "capabilities": ["code generation", "code review", "debugging"],
        "system_prompt": "You are a software development expert focused on writing clean, efficient, and well-documented code."
    }
    
    print("\n=== Registering Specialized Agents ===")
    for agent_info in [research_agent, writer_agent, code_agent]:
        result = orchestrator._handle_register_agent(**agent_info)
        print(result)
    
    print("\n=== Checking Agent Status ===")
    print(orchestrator._handle_check_status())
    
    print("\n=== Testing Complex Task Orchestration ===")
    complex_task = """
    Create a blog post about the latest developments in AI technology:
    1. Research recent AI breakthroughs
    2. Write an engaging article
    3. Include some example code snippets
    """
    
    result = orchestrator.orchestrate(complex_task)
    print("\nFinal Result:", result)

if __name__ == "__main__":
    main() 