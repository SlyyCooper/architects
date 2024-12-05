from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass

@dataclass
class Tool:
    """Represents a tool that can be used by the agent."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Optional[Callable] = None

@dataclass
class ToolConfig:
    """Configuration for tool usage."""
    type: str = "auto"  # Can be "auto", "any", or "tool"
    name: Optional[str] = None
    disable_parallel_tool_use: bool = False 