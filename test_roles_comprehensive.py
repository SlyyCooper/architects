from tangents.core.agent import Agent
from tangents.core.roles import RoleRegistry, RoleCategory, AgentRole, RoleCapability
from tangents.core.tool_types import Tool
import json

def create_mock_tools():
    """Create mock tools for testing."""
    return [
        Tool(
            name="code_edit",
            description="Edit code files",
            input_schema={"type": "object"}
        ),
        Tool(
            name="code_review",
            description="Review code changes",
            input_schema={"type": "object"}
        ),
        Tool(
            name="run_tests",
            description="Run test suites",
            input_schema={"type": "object"}
        ),
        Tool(
            name="search",
            description="Search for information",
            input_schema={"type": "object"}
        ),
        Tool(
            name="analyze_data",
            description="Analyze data sets",
            input_schema={"type": "object"}
        ),
        Tool(
            name="verify_facts",
            description="Verify information accuracy",
            input_schema={"type": "object"}
        )
    ]

def test_role_creation():
    """Test creating and validating roles."""
    print("\n=== Testing Role Creation ===")
    
    # Create a custom role
    custom_role = AgentRole(
        name="ai_specialist",
        category=RoleCategory.CUSTOM,
        description="AI/ML specialist with deep learning expertise",
        capabilities=[
            RoleCapability(
                name="model_training",
                description="Train and fine-tune AI models",
                required_tools={"analyze_data"}
            )
        ],
        base_prompt_template="""You are an AI/ML specialist focused on {framework}.
        Your expertise includes {specialty} and you excel at {task_type} tasks.""",
        default_tools=["analyze_data"],
        specialization_options={
            "framework": ["PyTorch", "TensorFlow", "JAX"],
            "specialty": ["computer_vision", "nlp", "reinforcement_learning"],
            "task_type": ["training", "optimization", "deployment"]
        },
        personality_traits=[
            "Innovative thinker",
            "Data-driven decision maker",
            "Optimization enthusiast"
        ]
    )
    
    print("Custom role created:", custom_role.name)
    print("Specialization options:", custom_role.specialization_options)

def test_role_registry():
    """Test the role registry functionality."""
    print("\n=== Testing Role Registry ===")
    
    registry = RoleRegistry()
    
    # List available roles by category
    for category in RoleCategory:
        roles = registry.list_roles(category)
        print(f"{category.value} roles:", roles)
    
    # Test role retrieval
    dev_role = registry.get_role("developer")
    print("\nDeveloper role capabilities:", [cap.name for cap in dev_role.capabilities])

def test_specialization():
    """Test role specialization and prompt generation."""
    print("\n=== Testing Role Specialization ===")
    
    registry = RoleRegistry()
    dev_role = registry.get_role("developer")
    
    # Test different specializations
    specializations = [
        {
            "language": "Python",
            "specialty": "backend"
        },
        {
            "language": "TypeScript",
            "specialty": "frontend"
        }
    ]
    
    for spec in specializations:
        prompt = dev_role.generate_prompt(spec)
        print(f"\nPrompt for {spec['language']} {spec['specialty']} developer:")
        print(prompt)

def test_validation():
    """Test role validation and error handling."""
    print("\n=== Testing Validation ===")
    
    registry = RoleRegistry()
    dev_role = registry.get_role("developer")
    
    # Test tool validation
    available_tools = create_mock_tools()
    is_valid = dev_role.validate(available_tools, set())
    print("Role validation with tools:", "Passed" if is_valid else "Failed")
    
    # Test invalid specialization
    try:
        dev_role.generate_prompt({"invalid": "value"})
    except ValueError as e:
        print("Caught invalid specialization:", str(e))

def test_persistence():
    """Test saving and loading roles."""
    print("\n=== Testing Role Persistence ===")
    
    registry = RoleRegistry()
    
    # Save roles
    registry.save_roles("test_roles.json")
    print("Roles saved to test_roles.json")
    
    # Load roles in new registry
    new_registry = RoleRegistry()
    new_registry.load_roles("test_roles.json")
    print("Loaded roles:", new_registry.list_roles())
    
    # Verify loaded roles
    original_roles = set(registry.list_roles())
    loaded_roles = set(new_registry.list_roles())
    print("Roles preserved correctly:", original_roles == loaded_roles)

def test_agent_creation():
    """Test creating agents with roles."""
    print("\n=== Testing Agent Creation ===")
    
    registry = RoleRegistry()
    available_tools = create_mock_tools()
    
    # Create specialized agents
    roles_to_test = [
        ("developer", {"language": "Python", "specialty": "backend"}),
        ("researcher", {"field": "technology", "research_type": "qualitative"})
    ]
    
    for role_name, specialization in roles_to_test:
        role = registry.get_role(role_name)
        agent = Agent(
            name=f"{role_name.capitalize()}Agent",
            system_prompt=role.generate_prompt(specialization),
            tools=available_tools
        )
        print(f"\nCreated {agent.name}")
        print("System prompt:", agent.system_prompt)
        print("Available tools:", [tool.name for tool in agent.tools])

def main():
    """Run all tests."""
    tests = [
        test_role_creation,
        test_role_registry,
        test_specialization,
        test_validation,
        test_persistence,
        test_agent_creation
    ]
    
    for test in tests:
        test()
        print("\n" + "="*50)

if __name__ == "__main__":
    main() 