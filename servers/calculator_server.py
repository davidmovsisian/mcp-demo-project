"""
Weather MCP Server with ServerTool class.
"""
from dataclasses import dataclass
from numbers import Number
from typing import Any, Callable, Awaitable
import anyio
import click
import mcp.types as types
from mcp.server. lowlevel import Server
from jsonschema import validate, ValidationError as JsonSchemaValidationError

@dataclass
class ServerTool:
    """
    Server-side tool definition with metadata and handler.
    Extends MCP Tool concept to include execution logic.
    """
    name: str
    title: str
    description: str
    input_schema: dict
    handler:  Callable[[Number, Number], Awaitable[str]]
    
    def to_mcp_tool(self) -> types.Tool:
        """Convert to MCP Tool for client communication."""
        return types.Tool(
            name=self.name,
            title=self.title,
            description=self.description,
            inputSchema=self.input_schema
        )
    
    async def execute(self, arguments: dict) -> str:
        validate(instance=arguments, schema=self.input_schema)
        return await self.handler(arguments["a"], arguments["b"])
    
async def add_numbers(a, b) -> str:
    result = a + b
    return f"{a} + {b} = {result}"

async def subtract_numbers(a, b) -> str:
    result = a - b
    return f"{a} - {b} = {result}"

async def multiply_numbers(a, b) -> str:
    result = a * b
    return f"{a} * {b} = {result}"

async def divide_numbers(a, b) -> str:
    if b == 0:
        return "Error: Division by zero"
    result = a / b
    return f"{a} / {b} = {result}"


# Tool registry with ServerTool objects
TOOLS: dict[str, ServerTool] = {
    "add": ServerTool(
        name="add",
        title="Add Two Numbers",
        description="Add two numbers",
        input_schema={
            "type": "object",
            "required": ["a", "b"],
            "properties": {
                "a": {
                    "type": "number",
                    "description": "First number to add",
                },
                "b": {
                    "type": "number",
                    "description": "Second number to add",
                }
            },
        },
        handler=add_numbers
    ),
    
    "subtract": ServerTool(
        name="subtract",
        title="Subtract Two Numbers",
        description="Subtract two numbers",
        input_schema={
            "type": "object",
            "required": ["a", "b"],
            "properties": {
                "a": {
                    "type": "number",
                    "description": "Number to subtract from",
                },
                "b": {
                    "type": "number",
                    "description": "Number to subtract",
                }
            },
        },
        handler=subtract_numbers
    ),

    "multiply": ServerTool(
        name="multiply",
        title="Multiply Two Numbers",
        description="Multiply two numbers",
        input_schema={
            "type": "object",
            "required": ["a", "b"],
            "properties": {
                "a": {
                    "type": "number",
                    "description": "First number to multiply",
                },
                "b": {
                    "type": "number",
                    "description": "Second number to multiply",
                }
            },
        },
        handler=multiply_numbers
    ),

    "divide": ServerTool(
        name="divide",
        title="Divide Two Numbers",
        description="Divide two numbers",
        input_schema={
            "type": "object",
            "required": ["a", "b"],
            "properties": {
                "a": {
                    "type": "number",
                    "description": "Numerator",
                },
                "b": {
                    "type": "number",
                    "description": "Denominator",
                }
            },
        },
        handler=divide_numbers
    )
}


@click.command()
@click.option("--port", default=8001, help="Port to listen on for SSE transport")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type (stdio or sse)",
)
def main(port:  int, transport: str) -> int:
    """Start the Calculator MCP server."""
    app = Server("calculator-server")
    
    @app.call_tool()
    async def call_tool(name:  str, arguments: dict[str, Any]) -> list[types.ContentBlock]:
        """Handle tool execution with automatic validation."""
        if name not in TOOLS:
            raise ValueError(f"Unknown tool: {name}")
        
        tool = TOOLS[name]
        
        try:
            result = await tool.execute(arguments)
            return [types.TextContent(type="text", text=result)]
        except JsonSchemaValidationError as e:
            raise ValueError(f"Invalid arguments for tool '{name}': {e. message}")
    
    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        """Provide list of available tools."""
        return [tool.to_mcp_tool() for tool in TOOLS.values()]
    
    # Transport setup and server start
    if transport == "sse":
        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.requests import Request
        from starlette.responses import Response
        from starlette.routing import Mount, Route
        
        sse = SseServerTransport("/messages/")
        
        async def handle_sse(request: Request) -> Response:
            async with sse. connect_sse(
                request. scope, request.receive, request._send
            ) as streams:
                await app.run(
                    streams[0], streams[1], app. create_initialization_options()
                )
            return Response()
        
        starlette_app = Starlette(
            debug=True,
            routes=[
                Route("/sse", endpoint=handle_sse, methods=["GET"]),
                Mount("/messages/", app=sse. handle_post_message),
            ],
        )
        
        import uvicorn
        print(f"🌤️ Weather Server starting on http://127.0.0.1:{port} (SSE transport)")
        uvicorn.run(starlette_app, host="127.0.0.1", port=port)
    else:  # stdio transport
        from mcp.server.stdio import stdio_server
        
        async def run_stdio():
            # Print to stderr (stdout is reserved for MCP protocol)
            print("🌤️ Calculator Server starting (STDIO transport)")
            async with stdio_server() as streams:
                await app.run(
                    streams[0], streams[1], app.create_initialization_options()
                )
        
        anyio.run(run_stdio)
    
    return 0


if __name__ == "__main__": 
    main()