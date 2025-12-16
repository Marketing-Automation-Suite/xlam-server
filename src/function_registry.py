"""
Function Registry
Manages available functions that can be called by the AI
"""

from typing import Dict, List, Any, Callable, Optional
import logging

logger = logging.getLogger(__name__)


class FunctionRegistry:
    """Registry for available functions"""
    
    def __init__(self):
        self._functions: Dict[str, Dict[str, Any]] = {}
        self._handlers: Dict[str, Callable] = {}
    
    def register_function(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        handler: Optional[Callable] = None
    ):
        """
        Register a function that can be called by the AI.
        
        Args:
            name: Function name
            description: Function description
            parameters: Function parameters schema
            handler: Optional handler function
        """
        self._functions[name] = {
            "name": name,
            "description": description,
            "parameters": parameters
        }
        
        if handler:
            self._handlers[name] = handler
        
        logger.info(f"Registered function: {name}")
    
    def get_function(self, name: str) -> Optional[Dict[str, Any]]:
        """Get function definition by name"""
        return self._functions.get(name)
    
    def list_functions(self) -> List[Dict[str, Any]]:
        """List all registered functions"""
        return list(self._functions.values())
    
    def execute_function(self, name: str, arguments: Dict[str, Any]) -> Any:
        """
        Execute a function by name with given arguments.
        
        Args:
            name: Function name
            arguments: Function arguments
        
        Returns:
            Function execution result
        """
        if name not in self._functions:
            raise ValueError(f"Function not found: {name}")
        
        if name in self._handlers:
            handler = self._handlers[name]
            return handler(**arguments)
        else:
            # Function registered but no handler - return function call info
            return {
                "function": name,
                "arguments": arguments,
                "status": "registered_but_no_handler"
            }
    
    def get_tools_definition(self) -> List[Dict[str, Any]]:
        """
        Get tools definition in OpenAI function calling format.
        
        Returns:
            List of tool definitions
        """
        tools = []
        for func in self._functions.values():
            tools.append({
                "type": "function",
                "function": {
                    "name": func["name"],
                    "description": func["description"],
                    "parameters": func["parameters"]
                }
            })
        return tools


# Global function registry instance
function_registry = FunctionRegistry()

