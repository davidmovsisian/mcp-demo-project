# MCP Prompts and Resources Implementation

> **Note:** The folder is named `Promts_And_Resources` (with "Promts" instead of "Prompts") as specified in the project requirements.

Complete Python implementation of MCP (Model Context Protocol) server with prompts, resources, and tools, integrated with OpenAI.

## Features

- **Prompts**: Reusable templates for LLM interactions (code-review, sprint-summary, bug-analysis)
- **Resources**: URI-addressable data sources (tasks, codebase, summaries)
- **Tools**: Executable actions (update_task_status, add_task)
- **OpenAI Integration**: Seamless integration with GPT-4

## Setup

```bash
cd Promts_And_Resources
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
export OPENAI_API_KEY='your-key-here'
```

## Run

```bash
# Run client (automatically starts server)
python mcp_client.py

# Or run server standalone
python mcp_server.py
```

## Usage with Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "project-assistant": {
      "command": "python",
      "args": ["/absolute/path/to/Promts_And_Resources/mcp_server.py"]
    }
  }
}
```

## Architecture

- `mcp_server.py` - MCP server with prompts, resources, and tools
- `mcp_client.py` - Client demonstrating OpenAI integration
- `requirements.txt` - Python dependencies
