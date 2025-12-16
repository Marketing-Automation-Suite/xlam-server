"""
MCP Configuration Functions
Register MCP tools as callable functions for the AI agent
"""

import os
import httpx
import logging
from typing import Dict, Any, Optional, List

from ..function_registry import function_registry

logger = logging.getLogger(__name__)

# MCP Configuration Server URL
MCP_CONFIG_SERVER_URL = os.getenv(
    "MCP_CONFIG_SERVER_URL",
    "http://mcp-config-server:8001"
)


def register_mcp_functions():
    """Register all MCP configuration functions with the function registry"""
    
    # Discover Available Services
    function_registry.register_function(
        name="mcp_discover_services",
        description="Discover what external services can be configured for marketing automation. Filter by category: lead_generation, email, data_enrichment, or 'all'.",
        parameters={
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["lead_generation", "email", "data_enrichment", "all"],
                    "description": "Category of services to discover",
                    "default": "all"
                }
            }
        },
        handler=discover_services_handler
    )
    
    # Get Service Information
    function_registry.register_function(
        name="mcp_get_service_info",
        description="Get detailed information about a specific service including capabilities, pricing, and requirements.",
        parameters={
            "type": "object",
            "properties": {
                "service_name": {
                    "type": "string",
                    "description": "Service identifier (e.g., 'linkedin', 'sendgrid', 'hunter_io')"
                }
            },
            "required": ["service_name"]
        },
        handler=get_service_info_handler
    )
    
    # Configure Service
    function_registry.register_function(
        name="mcp_configure_service",
        description="Configure an external service with API credentials. The AI will guide you through the process step-by-step.",
        parameters={
            "type": "object",
            "properties": {
                "service_name": {
                    "type": "string",
                    "description": "Service identifier (e.g., 'linkedin', 'sendgrid')"
                },
                "credentials": {
                    "type": "object",
                    "description": "Service credentials (API keys, tokens, etc.)"
                },
                "settings": {
                    "type": "object",
                    "description": "Optional service-specific settings"
                },
                "config_name": {
                    "type": "string",
                    "description": "Configuration name (default: 'default')",
                    "default": "default"
                }
            },
            "required": ["service_name", "credentials"]
        },
        handler=configure_service_handler
    )
    
    # Test Service Connection
    function_registry.register_function(
        name="mcp_test_service",
        description="Test if a configured service connection is working. Validates credentials and API access.",
        parameters={
            "type": "object",
            "properties": {
                "service_name": {
                    "type": "string",
                    "description": "Service identifier"
                },
                "config_id": {
                    "type": "integer",
                    "description": "Optional configuration ID to test specific config"
                }
            },
            "required": ["service_name"]
        },
        handler=test_service_handler
    )
    
    # List Configured Services
    function_registry.register_function(
        name="mcp_list_services",
        description="List all currently configured services and their status (active, failed, pending).",
        parameters={
            "type": "object",
            "properties": {}
        },
        handler=list_services_handler
    )
    
    # Update Service Configuration
    function_registry.register_function(
        name="mcp_update_service_config",
        description="Update configuration for an existing service. Can update credentials or settings.",
        parameters={
            "type": "object",
            "properties": {
                "service_name": {
                    "type": "string",
                    "description": "Service identifier"
                },
                "updates": {
                    "type": "object",
                    "description": "Configuration updates (credentials, settings, etc.)"
                }
            },
            "required": ["service_name", "updates"]
        },
        handler=update_service_config_handler
    )
    
    # Get Configuration Guide
    function_registry.register_function(
        name="mcp_get_config_guide",
        description="Get step-by-step guide for configuring a specific service. Includes where to find API keys and setup instructions.",
        parameters={
            "type": "object",
            "properties": {
                "service_name": {
                    "type": "string",
                    "description": "Service identifier"
                }
            },
            "required": ["service_name"]
        },
        handler=get_config_guide_handler
    )
    
    # Search Marketplace
    function_registry.register_function(
        name="mcp_search_marketplace",
        description="Search marketplace for services by use case, integration type, or category.",
        parameters={
            "type": "object",
            "properties": {
                "use_case": {
                    "type": "string",
                    "description": "Search by use case (e.g., 'lead generation', 'email marketing')"
                },
                "integration_type": {
                    "type": "string",
                    "description": "Search by integration type"
                },
                "category": {
                    "type": "string",
                    "enum": ["lead_generation", "email", "data_enrichment"],
                    "description": "Filter by category"
                }
            }
        },
        handler=search_marketplace_handler
    )
    
    logger.info("MCP configuration functions registered")


# Handler functions

def discover_services_handler(category: str = "all") -> Dict[str, Any]:
    """Handler for discovering services"""
    try:
        with httpx.Client() as client:
            response = client.get(
                f"{MCP_CONFIG_SERVER_URL}/mcp/tools/discover_services",
                params={"category": category},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error discovering services: {str(e)}")
        return {
            "success": False,
            "message": f"Error discovering services: {str(e)}",
            "error": str(e)
        }


def get_service_info_handler(service_name: str) -> Dict[str, Any]:
    """Handler for getting service information"""
    try:
        with httpx.Client() as client:
            response = client.get(
                f"{MCP_CONFIG_SERVER_URL}/mcp/tools/get_service_info",
                params={"service_name": service_name},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error getting service info: {str(e)}")
        return {
            "success": False,
            "message": f"Error getting service info: {str(e)}",
            "error": str(e)
        }


def configure_service_handler(
    service_name: str,
    credentials: Dict[str, Any],
    settings: Optional[Dict[str, Any]] = None,
    config_name: str = "default"
) -> Dict[str, Any]:
    """Handler for configuring a service"""
    try:
        with httpx.Client() as client:
            response = client.post(
                f"{MCP_CONFIG_SERVER_URL}/mcp/tools/configure_service",
                json={
                    "service_name": service_name,
                    "credentials": credentials,
                    "settings": settings or {},
                    "config_name": config_name
                },
                timeout=60.0  # Longer timeout for configuration
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error configuring service: {str(e)}")
        return {
            "success": False,
            "message": f"Error configuring service: {str(e)}",
            "error": str(e)
        }


def test_service_handler(
    service_name: str,
    config_id: Optional[int] = None
) -> Dict[str, Any]:
    """Handler for testing service connection"""
    try:
        with httpx.Client() as client:
            params = {"service_name": service_name}
            if config_id:
                params["config_id"] = config_id
            
            response = client.post(
                f"{MCP_CONFIG_SERVER_URL}/mcp/tools/test_service_connection",
                params=params,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error testing service: {str(e)}")
        return {
            "success": False,
            "message": f"Error testing service: {str(e)}",
            "error": str(e)
        }


def list_services_handler() -> Dict[str, Any]:
    """Handler for listing configured services"""
    try:
        with httpx.Client() as client:
            response = client.get(
                f"{MCP_CONFIG_SERVER_URL}/mcp/tools/list_configured_services",
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error listing services: {str(e)}")
        return {
            "success": False,
            "message": f"Error listing services: {str(e)}",
            "error": str(e)
        }


def update_service_config_handler(
    service_name: str,
    updates: Dict[str, Any]
) -> Dict[str, Any]:
    """Handler for updating service configuration"""
    try:
        with httpx.Client() as client:
            response = client.post(
                f"{MCP_CONFIG_SERVER_URL}/mcp/tools/update_service_config",
                params={"service_name": service_name},
                json={"updates": updates},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error updating service config: {str(e)}")
        return {
            "success": False,
            "message": f"Error updating service config: {str(e)}",
            "error": str(e)
        }


def get_config_guide_handler(service_name: str) -> Dict[str, Any]:
    """Handler for getting configuration guide"""
    try:
        with httpx.Client() as client:
            response = client.get(
                f"{MCP_CONFIG_SERVER_URL}/mcp/tools/get_configuration_guide",
                params={"service_name": service_name},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error getting config guide: {str(e)}")
        return {
            "success": False,
            "message": f"Error getting config guide: {str(e)}",
            "error": str(e)
        }


def search_marketplace_handler(
    use_case: Optional[str] = None,
    integration_type: Optional[str] = None,
    category: Optional[str] = None
) -> Dict[str, Any]:
    """Handler for searching marketplace"""
    try:
        with httpx.Client() as client:
            params = {}
            if use_case:
                params["use_case"] = use_case
            if integration_type:
                params["integration_type"] = integration_type
            if category:
                params["category"] = category
            
            response = client.get(
                f"{MCP_CONFIG_SERVER_URL}/mcp/tools/search_marketplace",
                params=params,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error searching marketplace: {str(e)}")
        return {
            "success": False,
            "message": f"Error searching marketplace: {str(e)}",
            "error": str(e)
        }

