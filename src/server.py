"""
AI Function Calling Server - FastAPI Entrypoint
Model-agnostic function calling service with OpenAI-compatible API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import logging

from .formatting import format_tools_for_model
from .engine import call_model
from .function_registry import FunctionRegistry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Function Calling Server",
    version="1.0.0",
    description="Model-agnostic AI function calling service"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize function registry
function_registry = FunctionRegistry()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: Optional[str] = None
    messages: List[ChatMessage]
    tools: Optional[List[Dict[str, Any]]] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]


@app.get("/health")
async def health():
    """Basic health check"""
    return {"status": "healthy", "service": "ai-function-calling-server"}


@app.get("/health/ready")
async def readiness():
    """Readiness probe - check if service can accept requests"""
    # Add model availability check here
    return {"status": "ready"}


@app.get("/health/live")
async def liveness():
    """Liveness probe - check if service is alive"""
    return {"status": "alive"}


@app.get("/v1/functions")
async def list_functions():
    """List all available functions"""
    return {
        "functions": function_registry.list_functions(),
        "count": len(function_registry.list_functions())
    }


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """
    OpenAI-compatible chat completions endpoint with function calling support.
    
    Supports model-agnostic function calling with flexible tool formatting.
    """
    try:
        # Get model configuration
        model_config = get_model_config(request.model)
        
        # Format tools for the model
        formatted_tools = None
        if request.tools:
            format_type = model_config.get("tool_format", "json")
            formatted_tools = format_tools_for_model(request.tools, format_type)
        
        # Build prompt from messages
        prompt = build_prompt_from_messages(request.messages)
        
        # Call model
        response = call_model(
            prompt=prompt,
            tools=formatted_tools,
            model_config=model_config,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in chat completion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def get_model_config(model_name: Optional[str] = None) -> Dict[str, Any]:
    """Get model configuration from environment or config file"""
    # Default configuration
    default_config = {
        "backend": os.getenv("MODEL_BACKEND", "ollama"),
        "model_name": model_name or os.getenv("MODEL_NAME", "default"),
        "base_url": os.getenv("MODEL_BASE_URL", "http://localhost:11434"),
        "tool_format": os.getenv("TOOL_FORMAT", "json"),
        "use_raw_mode": os.getenv("USE_RAW_MODE", "false").lower() == "true"
    }
    
    # Load from config file if exists
    # TODO: Implement config file loading
    
    return default_config


def build_prompt_from_messages(messages: List[ChatMessage]) -> str:
    """Build prompt string from message list"""
    prompt_parts = []
    for msg in messages:
        prompt_parts.append(f"{msg.role}: {msg.content}")
    return "\n".join(prompt_parts)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

