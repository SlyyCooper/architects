from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path
from .tool_types import Tool

class RoleCategory(Enum):
    """Categories for agent roles to ensure proper organization."""
    GENERAL = "general"
    CODING = "coding"
    RESEARCH = "research"
    WRITING = "writing"
    ANALYSIS = "analysis"
    CREATIVE = "creative"
    ORCHESTRATION = "orchestration"
    CUSTOM = "custom"

@dataclass
class RoleCapability:
    """Defines a specific capability with validation."""
    name: str
    description: str
    required_tools: Set[str] = field(default_factory=set)
    required_permissions: Set[str] = field(default_factory=set)
    
    def validate(self, available_tools: List[Tool], permissions: Set[str]) -> bool:
        """Validate that all required tools and permissions are available."""
        available_tool_names = {tool.name for tool in available_tools}
        return (
            self.required_tools.issubset(available_tool_names) and
            self.required_permissions.issubset(permissions)
        )

@dataclass
class AgentRole:
    """Defines a specific role with its capabilities and requirements."""
    
    name: str
    category: RoleCategory
    description: str
    capabilities: List[RoleCapability]
    base_prompt_template: str
    default_tools: List[str] = field(default_factory=list)
    required_permissions: Set[str] = field(default_factory=set)
    personality_traits: List[str] = field(default_factory=list)
    specialization_options: Dict[str, List[str]] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate role configuration."""
        if not self.name:
            raise ValueError("Role name cannot be empty")
        if not self.description:
            raise ValueError("Role description cannot be empty")
        if not self.base_prompt_template:
            raise ValueError("Base prompt template cannot be empty")
    
    def generate_prompt(self, specialization: Optional[Dict[str, str]] = None) -> str:
        """Generate a complete system prompt for this role."""
        prompt = self.base_prompt_template
        
        if specialization:
            # Validate specialization options
            for key, value in specialization.items():
                if key not in self.specialization_options:
                    raise ValueError(f"Invalid specialization option: {key}")
                if value not in self.specialization_options[key]:
                    raise ValueError(f"Invalid value '{value}' for specialization '{key}'")
            
            # Apply specializations
            prompt = prompt.format(**specialization)
        
        # Add personality traits
        if self.personality_traits:
            traits_str = "\n".join(f"- {trait}" for trait in self.personality_traits)
            prompt += f"\n\nYour personality traits include:\n{traits_str}"
        
        return prompt
    
    def validate(self, available_tools: List[Tool], permissions: Set[str]) -> bool:
        """Validate that the role can be properly instantiated."""
        # Check all capabilities
        for capability in self.capabilities:
            if not capability.validate(available_tools, permissions):
                return False
        
        # Check default tools
        available_tool_names = {tool.name for tool in available_tools}
        if not set(self.default_tools).issubset(available_tool_names):
            return False
        
        # Check permissions
        if not self.required_permissions.issubset(permissions):
            return False
        
        return True

class RoleRegistry:
    """Central registry for managing and accessing agent roles."""
    
    def __init__(self):
        self._roles: Dict[str, AgentRole] = {}
        self._load_default_roles()
    
    def _load_default_roles(self):
        """Load the default set of roles."""
        # Developer Role
        self.register_role(AgentRole(
            name="developer",
            category=RoleCategory.CODING,
            description="Expert software developer with strong coding and problem-solving skills",
            capabilities=[
                RoleCapability(
                    name="code_generation",
                    description="Generate high-quality code",
                    required_tools={"code_edit", "code_review"}
                ),
                RoleCapability(
                    name="debugging",
                    description="Debug and fix code issues",
                    required_tools={"code_edit", "run_tests"}
                )
            ],
            base_prompt_template="""You are an expert software developer specialized in {language}.
            Your main focus is writing clean, efficient, and well-documented code.
            You excel at {specialty} development and follow best practices for {language}.
            """,
            default_tools=["code_edit", "code_review", "run_tests"],
            specialization_options={
                "language": ["Python", "JavaScript", "TypeScript", "Java", "C++", "Rust"],
                "specialty": ["backend", "frontend", "full-stack", "systems", "mobile"]
            },
            personality_traits=[
                "Detail-oriented",
                "Systematic problem solver",
                "Clear communicator"
            ]
        ))
        
        # Researcher Role
        self.register_role(AgentRole(
            name="researcher",
            category=RoleCategory.RESEARCH,
            description="Thorough researcher with strong analytical skills",
            capabilities=[
                RoleCapability(
                    name="data_analysis",
                    description="Analyze and interpret data",
                    required_tools={"search", "analyze_data"}
                ),
                RoleCapability(
                    name="fact_checking",
                    description="Verify information accuracy",
                    required_tools={"search", "verify_facts"}
                )
            ],
            base_prompt_template="""You are an expert researcher specialized in {field}.
            Your focus is on {research_type} research and analysis.
            You excel at finding and verifying information in {field}.
            """,
            default_tools=["search", "analyze_data", "verify_facts"],
            specialization_options={
                "field": ["technology", "science", "business", "academia"],
                "research_type": ["quantitative", "qualitative", "mixed-methods"]
            },
            personality_traits=[
                "Methodical",
                "Attention to detail",
                "Critical thinker"
            ]
        ))
    
    def register_role(self, role: AgentRole) -> None:
        """Register a new role or update an existing one."""
        if not isinstance(role, AgentRole):
            raise TypeError("Role must be an instance of AgentRole")
        self._roles[role.name] = role
    
    def get_role(self, name: str) -> AgentRole:
        """Get a role by name."""
        if name not in self._roles:
            raise ValueError(f"Role '{name}' not found")
        return self._roles[name]
    
    def list_roles(self, category: Optional[RoleCategory] = None) -> List[str]:
        """List available roles, optionally filtered by category."""
        if category:
            return [name for name, role in self._roles.items() 
                   if role.category == category]
        return list(self._roles.keys())
    
    def save_roles(self, path: str) -> None:
        """Save roles to a JSON file."""
        role_data = {
            name: {
                "name": role.name,
                "category": role.category.value,
                "description": role.description,
                "capabilities": [
                    {
                        "name": cap.name,
                        "description": cap.description,
                        "required_tools": list(cap.required_tools),
                        "required_permissions": list(cap.required_permissions)
                    }
                    for cap in role.capabilities
                ],
                "base_prompt_template": role.base_prompt_template,
                "default_tools": role.default_tools,
                "required_permissions": list(role.required_permissions),
                "personality_traits": role.personality_traits,
                "specialization_options": role.specialization_options
            }
            for name, role in self._roles.items()
        }
        
        with open(path, 'w') as f:
            json.dump(role_data, f, indent=2)
    
    def load_roles(self, path: str) -> None:
        """Load roles from a JSON file."""
        with open(path, 'r') as f:
            role_data = json.load(f)
        
        for name, data in role_data.items():
            capabilities = [
                RoleCapability(**cap_data)
                for cap_data in data["capabilities"]
            ]
            
            self.register_role(AgentRole(
                name=data["name"],
                category=RoleCategory(data["category"]),
                description=data["description"],
                capabilities=capabilities,
                base_prompt_template=data["base_prompt_template"],
                default_tools=data["default_tools"],
                required_permissions=set(data["required_permissions"]),
                personality_traits=data["personality_traits"],
                specialization_options=data["specialization_options"]
            )) 