from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from ..core.agent import Agent
from ..core.tool_types import Tool, ToolConfig
import json

@dataclass
class AgentInfo:
    """Information about a registered agent."""
    agent: Agent
    description: str
    capabilities: List[str]
    status: str = "idle"

class OrchestratorAgent(Agent):
    """A modern orchestrator agent that coordinates multiple specialized agents.
    
    Uses Claude-3-5-sonnet's latest features including:
    - Advanced tool use with parallel execution
    - Message batching for complex workflows
    - Prompt caching for improved performance
    - Structured output via tools
    """
    
    def __init__(
        self,
        name: str = "Orchestrator",
        system_prompt: Optional[str] = None,
        **kwargs
    ):
        # Default system prompt for orchestration
        if system_prompt is None:
            system_prompt = """You are a highly capable orchestrator agent that coordinates other specialized agents.
            Your role is to:
            1. Break down complex tasks into subtasks
            2. Assign subtasks to appropriate specialized agents
            3. Manage parallel execution when possible
            4. Aggregate and synthesize results
            5. Ensure quality and consistency
            6. Handle errors and retries gracefully
            
            Always think step-by-step and document your reasoning process.
            Use available tools to manage agents and track task progress.
            """
        
        super().__init__(name=name, system_prompt=system_prompt, **kwargs)
        
        # Initialize agent registry
        self.agents: Dict[str, AgentInfo] = {}
        
        # Add orchestration tools
        self._setup_orchestration_tools()
    
    def _setup_orchestration_tools(self):
        """Set up the default tools for orchestration."""
        
        # Tool for registering new agents
        self.add_tool(Tool(
            name="register_agent",
            description="""Register a new specialized agent for use in tasks.
            Provide the agent's name, description, and list of capabilities.
            Returns success/failure status.""",
            input_schema={
                "type": "object",
                "properties": {
                    "agent_name": {
                        "type": "string",
                        "description": "Unique name for the agent"
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed description of the agent's purpose"
                    },
                    "capabilities": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of agent's capabilities"
                    },
                    "system_prompt": {
                        "type": "string",
                        "description": "System prompt for the agent"
                    }
                },
                "required": ["agent_name", "description", "capabilities", "system_prompt"]
            },
            handler=self._handle_register_agent
        ))
        
        # Tool for delegating tasks
        self.add_tool(Tool(
            name="delegate_task",
            description="""Delegate a task to a registered agent.
            Specify the agent name and task details.
            Returns the agent's response.""",
            input_schema={
                "type": "object",
                "properties": {
                    "agent_name": {
                        "type": "string",
                        "description": "Name of the agent to delegate to"
                    },
                    "task": {
                        "type": "string",
                        "description": "Task description or query for the agent"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                        "description": "Task priority level"
                    }
                },
                "required": ["agent_name", "task"]
            },
            handler=self._handle_delegate_task
        ))
        
        # Tool for checking agent status
        self.add_tool(Tool(
            name="check_status",
            description="""Check the status of registered agents.
            Returns a list of agents and their current status.""",
            input_schema={
                "type": "object",
                "properties": {
                    "agent_name": {
                        "type": "string",
                        "description": "Optional: specific agent to check"
                    }
                }
            },
            handler=self._handle_check_status
        ))
        
        # Configure tools for parallel execution
        self.configure_tools(ToolConfig(
            type="auto",
            disable_parallel_tool_use=False  # Enable parallel tool use
        ))
    
    def _handle_register_agent(self, agent_name: str, description: str, 
                             capabilities: List[str], system_prompt: str) -> str:
        """Handle registration of a new agent."""
        try:
            # Create new agent instance
            new_agent = Agent(
                name=agent_name,
                system_prompt=system_prompt,
                model="claude-3-5-sonnet-20241022"
            )
            
            # Register agent info
            self.agents[agent_name] = AgentInfo(
                agent=new_agent,
                description=description,
                capabilities=capabilities
            )
            
            return f"Successfully registered agent: {agent_name}"
        except Exception as e:
            return f"Failed to register agent: {str(e)}"
    
    def _handle_delegate_task(self, agent_name: str, task: str, 
                            priority: str = "medium") -> str:
        """Handle task delegation to a specific agent."""
        if agent_name not in self.agents:
            return f"Error: Agent '{agent_name}' not found"
        
        agent_info = self.agents[agent_name]
        agent_info.status = "working"
        
        try:
            # Execute task
            response = agent_info.agent.think(task)
            agent_info.status = "idle"
            return response
        except Exception as e:
            agent_info.status = "error"
            return f"Error executing task: {str(e)}"
    
    def _handle_check_status(self, agent_name: Optional[str] = None) -> str:
        """Handle status check for agents."""
        if agent_name:
            if agent_name not in self.agents:
                return f"Error: Agent '{agent_name}' not found"
            agent_info = self.agents[agent_name]
            return json.dumps({
                "name": agent_name,
                "status": agent_info.status,
                "description": agent_info.description,
                "capabilities": agent_info.capabilities
            }, indent=2)
        
        # Return status of all agents
        return json.dumps({
            name: {
                "status": info.status,
                "description": info.description,
                "capabilities": info.capabilities
            }
            for name, info in self.agents.items()
        }, indent=2)
    
    def orchestrate(self, task: str) -> str:
        """Main method to orchestrate complex tasks using multiple agents."""
        return self.think(f"""Task to orchestrate: {task}
        
        Please:
        1. Analyze the task and break it down into subtasks
        2. Identify which agents should handle each subtask
        3. Execute subtasks in optimal order (parallel when possible)
        4. Synthesize results into a coherent response
        
        Show your work using thinking tags.""") 