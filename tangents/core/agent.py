from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
import anthropic
from anthropic import Anthropic
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text
from rich.live import Live
from .tool_types import Tool, ToolConfig

console = Console()

@dataclass
class Agent:
    """A simple but powerful agent class that interfaces with Claude-3-5-sonnet."""
    
    name: str
    system_prompt: str
    model: str = "claude-3-5-sonnet-20241022"
    temperature: float = 0.7
    max_tokens: int = 4096
    stream: bool = True
    parallel_execution: bool = True
    client: Optional[Anthropic] = None
    memory: Dict[str, Any] = field(default_factory=dict)
    tools: Dict[str, Tool] = field(default_factory=dict)
    tool_config: ToolConfig = field(default_factory=lambda: ToolConfig(disable_parallel_tool_use=False))
    
    def __post_init__(self):
        """Initialize the Anthropic client and configure tools based on parallel execution setting."""
        if self.client is None:
            self.client = Anthropic()
        
        # Configure tool parallelization based on parallel_execution setting
        self.tool_config.disable_parallel_tool_use = not self.parallel_execution
    
    def set_parallel_execution(self, enabled: bool) -> None:
        """Enable or disable parallel execution of tools."""
        self.parallel_execution = enabled
        self.tool_config.disable_parallel_tool_use = not enabled
        console.print(Panel(
            f"[dim]Parallel execution {'enabled' if enabled else 'disabled'}[/dim]",
            border_style="blue",
            padding=(0, 1),
            width=console.width
        ))
    
    def add_tool(self, tool: Tool) -> None:
        """Add a tool to the agent's toolkit."""
        self.tools[tool.name] = tool
        console.print(Panel(
            f"[dim]Added tool: {tool.name}[/dim]",
            border_style="green",
            padding=(0, 1),
            width=console.width
        ))
    
    def remove_tool(self, tool_name: str) -> None:
        """Remove a tool from the agent's toolkit."""
        if tool_name in self.tools:
            del self.tools[tool_name]
            console.print(Panel(
                f"[dim]Removed tool: {tool_name}[/dim]",
                border_style="yellow",
                padding=(0, 1),
                width=console.width
            ))
    
    def configure_tools(self, config: ToolConfig) -> None:
        """Configure how tools should be used."""
        self.tool_config = config
        console.print(Panel(
            f"[dim]Tool configuration updated: {config}[/dim]",
            border_style="blue",
            padding=(0, 1),
            width=console.width
        ))
    
    def _format_tools_for_api(self) -> List[Dict[str, Any]]:
        """Format tools for the Anthropic API."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema
            }
            for tool in self.tools.values()
        ]
    
    def _handle_tool_use(self, tool_use: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool use requests from Claude."""
        tool_name = tool_use["name"]
        tool_input = tool_use["input"]
        tool_id = tool_use["id"]
        
        if tool_name not in self.tools:
            return {
                "tool_use_id": tool_id,
                "content": f"Error: Tool '{tool_name}' not found",
                "is_error": True
            }
        
        tool = self.tools[tool_name]
        if tool.handler is None:
            return {
                "tool_use_id": tool_id,
                "content": f"Error: No handler defined for tool '{tool_name}'",
                "is_error": True
            }
        
        try:
            result = tool.handler(**tool_input)
            return {
                "tool_use_id": tool_id,
                "content": str(result)
            }
        except Exception as e:
            return {
                "tool_use_id": tool_id,
                "content": f"Error executing tool '{tool_name}': {str(e)}",
                "is_error": True
            }
    
    def think(self, message: str) -> str:
        """Process a message and return a response using Claude."""
        messages = [
            {
                "role": "user",
                "content": message
            }
        ]
        
        # Prepare API request with tools if available
        api_params = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": messages,
            "system": self.system_prompt,
            "stream": self.stream
        }
        
        # Add tools configuration if tools are available
        if self.tools:
            api_params["tools"] = self._format_tools_for_api()
            api_params["tool_choice"] = {
                "type": "auto",
                "disable_parallel_tool_use": not self.parallel_execution
            }
        
        # Create message with proper streaming configuration
        response = self.client.messages.create(**api_params)
        
        full_response = ""
        if self.stream:
            with Live("", console=console, refresh_per_second=10) as live:
                for chunk in response:
                    # Handle different types of streaming events
                    if hasattr(chunk, 'type'):
                        if chunk.type == 'message_start':
                            continue
                        elif chunk.type == 'content_block_start':
                            continue
                        elif chunk.type == 'content_block_delta':
                            if hasattr(chunk, 'delta') and hasattr(chunk.delta, 'text'):
                                content = chunk.delta.text
                                full_response += content
                                live.update(self._format_response(full_response, show_name=False))
                        elif chunk.type == 'tool_calls':
                            # Handle tool use request
                            for tool_call in chunk.tool_calls:
                                tool_result = self._handle_tool_use({
                                    "name": tool_call.name,
                                    "input": tool_call.parameters,
                                    "id": tool_call.id
                                })
                                messages.append({
                                    "role": "user",
                                    "content": [{"type": "tool_result", **tool_result}]
                                })
                            # Continue the conversation with tool result
                            response = self.client.messages.create(**api_params)
        else:
            full_response = response.content[0].text
            console.print(self._format_response(full_response))
        
        return full_response
    
    def _format_response(self, text: str, show_name: bool = True) -> Panel:
        """Format the response text as a Rich panel."""
        try:
            content = Markdown(text)
        except:
            content = Text(text)
        
        title = f"[bold magenta]{self.name}[/bold magenta]" if show_name else None
        return Panel(
            content,
            title=title,
            border_style="cyan",
            padding=(1, 2),
            width=console.width
        )
    
    def remember(self, key: str, value: Any) -> None:
        """Store information in agent's memory."""
        self.memory[key] = value
        console.print(Panel(
            f"[dim]Stored: {key}[/dim]",
            border_style="blue",
            padding=(0, 1),
            width=console.width
        ))
    
    def recall(self, key: str) -> Optional[Any]:
        """Retrieve information from agent's memory."""
        value = self.memory.get(key)
        if value:
            console.print(Panel(
                f"[dim]Recalled: {key} = {value}[/dim]",
                border_style="blue",
                padding=(0, 1),
                width=console.width
            ))
        return value 