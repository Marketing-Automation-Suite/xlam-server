# AI Function Calling Server

Model-agnostic AI function calling service that exposes an OpenAI-compatible API.

## Features

- OpenAI-compatible `/v1/chat/completions` endpoint
- Model-agnostic design (supports vLLM, Ollama, OpenAI-compatible APIs)
- Flexible tool formatting (JSON, XML, function calling)
- Function registry and execution
- Health check endpoints

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your model configuration

# Run server
uvicorn src.server:app --host 0.0.0.0 --port 8000
```

## API Endpoints

- `POST /v1/chat/completions` - OpenAI-compatible chat completion
- `GET /v1/functions` - List available functions
- `GET /health` - Health check
- `GET /health/ready` - Readiness probe
- `GET /health/live` - Liveness probe

## Configuration

See `config/model-config.yaml` for model configuration options.

## Development

This service uses `shared-libraries` as a git submodule for common code.

