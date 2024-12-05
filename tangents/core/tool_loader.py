from pathlib import Path
from typing import Optional, Dict, Any, List, Callable, Set
import yaml
import importlib.util
import inspect
from functools import wraps
import logging
from rich.console import Console
from rich.panel import Panel
from .tool_types import Tool

console = Console()
logger = logging.getLogger(__name__)

class ToolLoadError(Exception):
    """Raised when there's an error loading a tool."""
    pass

class DynamicToolSystem:
    """Easy-to-use dynamic tool loading system with auto-discovery and decorator registration."""
    
    def __init__(self, tools_dir: str = "tools/", auto_load: bool = True):
        """Initialize the tool system.
        
        Args:
            tools_dir: Directory containing tool configurations and implementations
            auto_load: Whether to automatically load tools on initialization
        """
        self.tools_dir = Path(tools_dir)
        self.tools: Dict[str, Tool] = {}
        self.registered_handlers: Dict[str, Callable] = {}
        self._loaded_paths: Set[Path] = set()
        
        # Create tools directory if it doesn't exist
        self.tools_dir.mkdir(parents=True, exist_ok=True)
        
        if auto_load:
            self.load_all_tools()
    
    @staticmethod
    def register(name: Optional[str] = None, description: Optional[str] = None, 
                input_schema: Optional[Dict] = None):
        """Decorator for registering tool handlers.
        
        Example:
            @DynamicToolSystem.register(
                name="search",
                description="Search the web",
                input_schema={"type": "object", "properties": {...}}
            )
            def web_search(query: str):
                ...
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            
            # Store tool metadata
            wrapper._is_tool = True
            wrapper._tool_name = name or func.__name__
            wrapper._tool_description = description or func.__doc__ or ""
            wrapper._tool_schema = input_schema or {
                "type": "object",
                "properties": {
                    param: {"type": "string"}
                    for param in inspect.signature(func).parameters
                }
            }
            return wrapper
        return decorator
    
    def load_all_tools(self) -> None:
        """Load all tools from the tools directory and registered decorators."""
        try:
            # Load YAML configurations
            yaml_configs = list(self.tools_dir.glob("**/*.yaml"))
            if yaml_configs:
                console.print(Panel(
                    f"[bold green]Found {len(yaml_configs)} tool configurations[/bold green]",
                    title="Tool Discovery"
                ))
                
                for config_path in yaml_configs:
                    try:
                        self.load_tool_from_config(config_path)
                    except Exception as e:
                        logger.error(f"Error loading tool from {config_path}: {str(e)}")
            
            # Load Python modules
            py_files = list(self.tools_dir.glob("**/*.py"))
            if py_files:
                console.print(Panel(
                    f"[bold blue]Found {len(py_files)} Python modules[/bold blue]",
                    title="Module Discovery"
                ))
                
                for py_path in py_files:
                    try:
                        self.load_tools_from_module(py_path)
                    except Exception as e:
                        logger.error(f"Error loading module {py_path}: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error during tool loading: {str(e)}")
            raise ToolLoadError(f"Failed to load tools: {str(e)}")
    
    def load_tool_from_config(self, config_path: Path) -> None:
        """Load a tool from a YAML configuration file."""
        if config_path in self._loaded_paths:
            return
        
        try:
            with open(config_path) as f:
                config = yaml.safe_load(f)
            
            # Validate required fields
            required_fields = {"name", "description", "handler"}
            missing_fields = required_fields - set(config.keys())
            if missing_fields:
                raise ValueError(f"Missing required fields: {missing_fields}")
            
            # Import handler
            handler = self._import_handler(config["handler"])
            
            # Create and register tool
            tool = Tool(
                name=config["name"],
                description=config["description"],
                input_schema=config.get("input_schema", {}),
                handler=handler
            )
            
            self.tools[tool.name] = tool
            self._loaded_paths.add(config_path)
            
            console.print(f"[green]Loaded tool:[/green] {tool.name}")
        
        except Exception as e:
            logger.error(f"Error loading {config_path}: {str(e)}")
            raise ToolLoadError(f"Failed to load tool config: {str(e)}")
    
    def load_tools_from_module(self, module_path: Path) -> None:
        """Load tools from a Python module using decorators."""
        if module_path in self._loaded_paths:
            return
        
        try:
            # Import module
            spec = importlib.util.spec_from_file_location(
                module_path.stem, module_path
            )
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not load module: {module_path}")
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find decorated functions
            for name, obj in inspect.getmembers(module):
                if hasattr(obj, '_is_tool'):
                    tool = Tool(
                        name=obj._tool_name,
                        description=obj._tool_description,
                        input_schema=obj._tool_schema,
                        handler=obj
                    )
                    self.tools[tool.name] = tool
                    console.print(f"[blue]Loaded decorated tool:[/blue] {tool.name}")
            
            self._loaded_paths.add(module_path)
        
        except Exception as e:
            logger.error(f"Error loading module {module_path}: {str(e)}")
            raise ToolLoadError(f"Failed to load module: {str(e)}")
    
    def _import_handler(self, handler_path: str) -> Callable:
        """Import a handler function from a module path."""
        try:
            module_path, func_name = handler_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            return getattr(module, func_name)
        except Exception as e:
            raise ImportError(f"Could not import handler {handler_path}: {str(e)}")
    
    def get_tool(self, name: str) -> Tool:
        """Get a tool by name."""
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found")
        return self.tools[name]
    
    def list_tools(self) -> List[str]:
        """List all available tools."""
        return list(self.tools.keys())
    
    def reload_tools(self) -> None:
        """Reload all tools, clearing existing registrations."""
        self.tools.clear()
        self._loaded_paths.clear()
        self.load_all_tools()
    
    def create_tool_template(self, name: str, template_type: str = "basic") -> None:
        """Create a new tool from a template."""
        templates = {
            "basic": """name: {name}
description: Description of the tool
handler: module.function
input_schema:
  type: object
  properties:
    param1:
      type: string
      description: Parameter description
  required: [param1]
""",
            "python": """from tangents.core.tool_loader import DynamicToolSystem

@DynamicToolSystem.register(
    name="{name}",
    description="Description of the tool",
    input_schema={{
        "type": "object",
        "properties": {{
            "param1": {{
                "type": "string",
                "description": "Parameter description"
            }}
        }},
        "required": ["param1"]
    }}
)
def {name}_handler(param1: str):
    \"\"\"Tool implementation.\"\"\"
    pass
"""
        }
        
        if template_type not in templates:
            raise ValueError(f"Unknown template type: {template_type}")
        
        # Create appropriate file
        if template_type == "basic":
            file_path = self.tools_dir / f"{name}.yaml"
        else:
            file_path = self.tools_dir / f"{name}.py"
        
        # Don't overwrite existing files
        if file_path.exists():
            raise FileExistsError(f"Tool file already exists: {file_path}")
        
        # Write template
        template = templates[template_type].format(name=name)
        with open(file_path, 'w') as f:
            f.write(template)
        
        console.print(Panel(
            f"[bold green]Created new tool template:[/bold green] {file_path}",
            title="Tool Creation"
        )) 