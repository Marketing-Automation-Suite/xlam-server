# AI Function Calling Server API

## Overview

Model-agnostic AI function calling service with OpenAI-compatible API.

## Endpoints

### Health Checks

#### GET /health
Basic health check.

**Response:**
```json
{
  "status": "healthy",
  "service": "ai-function-calling-server"
}
```

#### GET /health/ready
Readiness probe.

#### GET /health/live
Liveness probe.

### Function Management

#### GET /v1/functions
List all available functions.

**Response:**
```json
{
  "functions": [...],
  "count": 5
}
```

### Chat Completions

#### POST /v1/chat/completions
OpenAI-compatible chat completion endpoint.

**Request:**
```json
{
  "model": "optional-model-name",
  "messages": [
    {"role": "user", "content": "Create a lead for John Doe"}
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "crm_create_lead",
        "description": "Create a new lead",
        "parameters": {
          "type": "object",
          "properties": {
            "name": {"type": "string"},
            "email": {"type": "string"}
          }
        }
      }
    }
  ],
  "temperature": 0.7,
  "max_tokens": 1000
}
```

**Response:**
```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "default",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": null,
        "function_call": {
          "name": "crm_create_lead",
          "arguments": "{\"name\": \"John Doe\", \"email\": \"john@example.com\"}"
        }
      },
      "finish_reason": "function_call"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

## Configuration

The server supports multiple model backends:

- **Ollama**: Local model serving
- **vLLM**: High-performance inference
- **OpenAI-compatible**: Any OpenAI-compatible API

Configure via environment variables or `config/model-config.yaml`.

