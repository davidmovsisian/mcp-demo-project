# MCP Demo Project

A demonstration project with two MCP servers and two clients. 

## Project Structure

- `servers/` - MCP server implementations
  - `weather_server.py` - Weather information service
  - `calculator_server.py` - Mathematical calculator service
- `clients/` - MCP client implementations
  - `stdio_client.py` - Client using STDIO transport
  - `sse_client.py` - Client using SSE transport

## Installation

```bash
# Install uv package manager
curl -LsSf https://astral.sh/uv/install. sh | sh

# Install project dependencies
uv sync
```

## Usage

### Running Servers

```bash
# Weather server (STDIO)
uv run mcp-weather

# Weather server (SSE)
uv run mcp-weather --transport sse --port 8000

# Calculator server (STDIO)
uv run mcp-calculator

# Calculator server (SSE)
uv run mcp-calculator --transport sse --port 8001
```

### Running Clients

```bash
# STDIO client
uv run stdio-client

# SSE client
uv run sse-client
```

## Development

```bash
# Install development dependencies
uv sync --group dev

# Run tests
uv run pytest

# Format code
uv run ruff format

# Type check
uv run pyright
```