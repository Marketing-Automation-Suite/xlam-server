"""
Model Engine - Model-Agnostic Interface
Supports multiple model backends: vLLM, Ollama, OpenAI-compatible APIs
"""

from typing import Dict, Any, Optional
import os
import logging
import httpx
import json

logger = logging.getLogger(__name__)


def call_model(
    prompt: str,
    tools: Optional[Any] = None,
    model_config: Dict[str, Any] = None,
    temperature: float = 0.7,
    max_tokens: int = 1000
) -> Dict[str, Any]:
    """
    Call AI model for function calling.
    
    Model-agnostic interface that supports:
    - vLLM
    - Ollama
    - OpenAI-compatible APIs
    - Custom model backends
    
    Args:
        prompt: User prompt
        tools: Formatted tools (format depends on model)
        model_config: Model-specific configuration
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
    
    Returns:
        Function call response in OpenAI-compatible format
    """
    if model_config is None:
        model_config = get_default_config()
    
    backend = model_config.get("backend", "ollama")
    
    if backend == "ollama":
        return call_ollama(prompt, tools, model_config, temperature, max_tokens)
    elif backend == "vllm":
        return call_vllm(prompt, tools, model_config, temperature, max_tokens)
    elif backend == "openai":
        return call_openai_compatible(prompt, tools, model_config, temperature, max_tokens)
    else:
        raise ValueError(f"Unsupported backend: {backend}")


def call_ollama(
    prompt: str,
    tools: Optional[Any],
    config: Dict[str, Any],
    temperature: float,
    max_tokens: int
) -> Dict[str, Any]:
    """Call Ollama API"""
    base_url = config.get("base_url", "http://localhost:11434")
    model_name = config.get("model_name", "default")
    use_raw = config.get("use_raw_mode", False)
    
    url = f"{base_url}/api/generate"
    
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens
        }
    }
    
    # Add tools if provided
    if tools:
        if isinstance(tools, str):
            # XML format - append to prompt
            payload["prompt"] = f"{prompt}\n\n{tools}"
        else:
            # JSON format - add to context
            payload["context"] = json.dumps(tools)
    
    if use_raw:
        payload["raw"] = True
    
    try:
        response = httpx.post(url, json=payload, timeout=30.0)
        response.raise_for_status()
        result = response.json()
        
        # Parse response and extract function call
        return parse_function_call_response(result, config)
        
    except Exception as e:
        logger.error(f"Ollama API error: {str(e)}")
        raise


def call_vllm(
    prompt: str,
    tools: Optional[Any],
    config: Dict[str, Any],
    temperature: float,
    max_tokens: int
) -> Dict[str, Any]:
    """Call vLLM API (OpenAI-compatible)"""
    base_url = config.get("base_url", "http://localhost:8000")
    model_name = config.get("model_name", "default")
    
    url = f"{base_url}/v1/chat/completions"
    
    messages = [{"role": "user", "content": prompt}]
    
    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    if tools:
        payload["tools"] = tools if isinstance(tools, list) else [tools]
    
    try:
        response = httpx.post(url, json=payload, timeout=30.0)
        response.raise_for_status()
        return response.json()
        
    except Exception as e:
        logger.error(f"vLLM API error: {str(e)}")
        raise


def call_openai_compatible(
    prompt: str,
    tools: Optional[Any],
    config: Dict[str, Any],
    temperature: float,
    max_tokens: int
) -> Dict[str, Any]:
    """Call OpenAI-compatible API"""
    base_url = config.get("base_url", "https://api.openai.com/v1")
    model_name = config.get("model_name", "gpt-3.5-turbo")
    api_key = config.get("api_key", os.getenv("OPENAI_API_KEY"))
    
    url = f"{base_url}/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    messages = [{"role": "user", "content": prompt}]
    
    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    if tools:
        payload["tools"] = tools if isinstance(tools, list) else [tools]
    
    try:
        response = httpx.post(url, json=payload, headers=headers, timeout=30.0)
        response.raise_for_status()
        return response.json()
        
    except Exception as e:
        logger.error(f"OpenAI-compatible API error: {str(e)}")
        raise


def parse_function_call_response(response: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse model response and extract function call information.
    
    Handles different response formats from different backends.
    """
    # Default OpenAI-compatible format
    if "choices" in response:
        return response
    
    # Ollama format - convert to OpenAI-compatible
    if "response" in response:
        # Extract function call from response text
        # This is a simplified parser - enhance based on actual model output
        return {
            "id": f"call_{hash(response.get('response', ''))}",
            "object": "chat.completion",
            "created": response.get("created_at", 0),
            "model": config.get("model_name", "unknown"),
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response.get("response", ""),
                    "function_call": extract_function_call(response.get("response", ""))
                },
                "finish_reason": "function_call" if extract_function_call(response.get("response", "")) else "stop"
            }],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }
    
    return response


def extract_function_call(text: str) -> Optional[Dict[str, Any]]:
    """
    Extract function call from model response text.
    
    This is a simplified extractor - enhance based on actual model output format.
    """
    # Look for JSON function calls in the response
    import re
    
    # Try to find JSON object with function call
    json_match = re.search(r'\{[^}]*"name"[^}]*\}', text)
    if json_match:
        try:
            return json.loads(json_match.group())
        except:
            pass
    
    return None


def get_default_config() -> Dict[str, Any]:
    """Get default model configuration"""
    return {
        "backend": os.getenv("MODEL_BACKEND", "ollama"),
        "model_name": os.getenv("MODEL_NAME", "default"),
        "base_url": os.getenv("MODEL_BASE_URL", "http://localhost:11434"),
        "tool_format": os.getenv("TOOL_FORMAT", "json"),
        "use_raw_mode": os.getenv("USE_RAW_MODE", "false").lower() == "true"
    }

