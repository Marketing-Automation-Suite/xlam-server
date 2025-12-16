"""
Tool Formatting Module
Converts tool definitions to various formats supported by different models
"""

from typing import List, Dict, Any
import json


def format_tools_for_model(tools: List[Dict[str, Any]], format_type: str = "json") -> Any:
    """
    Convert tool definitions to model-specific format.
    
    Supports multiple formats:
    - "json": Standard JSON format (default)
    - "xml": XML format for models requiring <tools>...</tools>
    - "function_calling": OpenAI function calling format
    
    Args:
        tools: List of tool definitions
        format_type: Output format ("json", "xml", "function_calling")
    
    Returns:
        Formatted tools in the requested format
    """
    if format_type == "xml":
        return json_tools_to_xml(tools)
    elif format_type == "function_calling":
        return {"tools": tools}
    else:
        # Standard JSON format
        return tools


def json_tools_to_xml(tools: List[Dict[str, Any]]) -> str:
    """
    Convert JSON tool definitions to XML format.
    
    Some models require function calls in XML format: <tools>...</tools>
    
    Args:
        tools: List of tool definitions in JSON format
    
    Returns:
        XML string with tools formatted
    """
    xml_parts = ["<tools>"]
    
    for tool in tools:
        func = tool.get("function", {})
        name = func.get("name", "")
        description = func.get("description", "")
        parameters = func.get("parameters", {})
        
        xml_parts.append(f"<tool name='{name}'>")
        xml_parts.append(f"<description>{description}</description>")
        
        if parameters:
            xml_parts.append("<parameters>")
            xml_parts.append(json.dumps(parameters))
            xml_parts.append("</parameters>")
        
        xml_parts.append("</tool>")
    
    xml_parts.append("</tools>")
    return "".join(xml_parts)


def xml_tools_to_json(xml_string: str) -> List[Dict[str, Any]]:
    """
    Convert XML tool format back to JSON (if needed for processing).
    
    Args:
        xml_string: XML string with tools
    
    Returns:
        List of tool definitions in JSON format
    """
    # TODO: Implement XML parsing if needed
    # For now, return empty list
    return []

