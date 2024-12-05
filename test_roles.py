from tangents.core.agent import Agent
from tangents.core.roles import RoleRegistry, RoleCategory
from tangents.core.tool_types import Tool

def main():
    # Initialize the role registry
    registry = RoleRegistry()
    
    print("\n=== Available Roles ===")
    print("All roles:", registry.list_roles())
    print("\nCoding roles:", registry.list_roles(RoleCategory.CODING))
    print("Research roles:", registry.list_roles(RoleCategory.RESEARCH))
    
    # Create a specialized developer agent
    dev_role = registry.get_role("developer")
    dev_specialization = {
        "language": "Python",
        "specialty": "backend"
    }
    
    # Create the specialized agent
    dev_agent = Agent(
        name="PythonDev",
        system_prompt=dev_role.generate_prompt(dev_specialization),
        tools=[Tool(name=tool_name, description="", input_schema={}) 
               for tool_name in dev_role.default_tools]
    )
    
    print("\n=== Developer Agent ===")
    print("System Prompt:", dev_agent.system_prompt)
    print("Tools:", [tool.name for tool in dev_agent.tools])
    
    # Create a specialized researcher agent
    research_role = registry.get_role("researcher")
    research_specialization = {
        "field": "technology",
        "research_type": "qualitative"
    }
    
    # Create the specialized agent
    research_agent = Agent(
        name="TechResearcher",
        system_prompt=research_role.generate_prompt(research_specialization),
        tools=[Tool(name=tool_name, description="", input_schema={}) 
               for tool_name in research_role.default_tools]
    )
    
    print("\n=== Researcher Agent ===")
    print("System Prompt:", research_agent.system_prompt)
    print("Tools:", [tool.name for tool in research_agent.tools])
    
    # Demonstrate error handling
    print("\n=== Error Handling ===")
    try:
        # Try invalid specialization
        dev_role.generate_prompt({"invalid_key": "value"})
    except ValueError as e:
        print("Caught invalid specialization:", str(e))
    
    try:
        # Try invalid role name
        registry.get_role("nonexistent_role")
    except ValueError as e:
        print("Caught invalid role:", str(e))
    
    # Save and load roles demonstration
    print("\n=== Save & Load Roles ===")
    registry.save_roles("roles.json")
    new_registry = RoleRegistry()
    new_registry.load_roles("roles.json")
    print("Roles successfully saved and loaded")
    print("Loaded roles:", new_registry.list_roles())

if __name__ == "__main__":
    main() 