"""
Weather MCP Server with ServerTool class.
"""
from dataclasses import dataclass
from typing import Any, Callable, Awaitable
import anyio
import click
import mcp.types as types
from mcp.server. lowlevel import Server
from jsonschema import validate, ValidationError as JsonSchemaValidationError


# Simulated weather data
WEATHER_DATA = {
    "new york": {"temp": 72, "condition": "Sunny", "humidity": 65},
    "london": {"temp":  59, "condition": "Cloudy", "humidity": 78},
    "tokyo": {"temp": 68, "condition": "Rainy", "humidity": 82},
    "paris": {"temp": 64, "condition": "Partly Cloudy", "humidity": 70},
    "sydney": {"temp": 75, "condition": "Clear", "humidity":  60},
}


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
    handler:  Callable[[str], Awaitable[str]]
    
    def to_mcp_tool(self) -> types.Tool:
        """Convert to MCP Tool for client communication."""
        return types.Tool(
            name=self.name,
            title=self.title,
            description=self.description,
            inputSchema=self. input_schema
        )
    
    async def execute(self, arguments: dict) -> str:
        """
        Validate and execute the tool.
        
        Args:
            arguments: Tool arguments from client
            
        Returns:
            Result string
            
        Raises:
            JsonSchemaValidationError: If arguments don't match schema
        """
        validate(instance=arguments, schema=self.input_schema)
        return await self.handler(arguments["city"])


async def get_weather_data(city: str) -> str:
    """Get current weather for a city."""
    city_lower = city.lower()
    
    if city_lower in WEATHER_DATA:
        data = WEATHER_DATA[city_lower]
        return (
            f"Weather in {city. title()}:\n"
            f"  Temperature: {data['temp']}°F\n"
            f"  Condition: {data['condition']}\n"
            f"  Humidity: {data['humidity']}%"
        )
    else:
        return f"Weather data not available for {city}.  Try:  New York, London, Tokyo, Paris, or Sydney."


async def get_forecast_data(city: str) -> str:
    """Get 5-day forecast for a city."""
    city_lower = city.lower()
    
    if city_lower in WEATHER_DATA:
        base_temp = WEATHER_DATA[city_lower]["temp"]
        return (
            f"5-Day Forecast for {city.title()}:\n"
            f"  Day 1: {base_temp}°F - Sunny\n"
            f"  Day 2: {base_temp + 2}°F - Partly Cloudy\n"
            f"  Day 3: {base_temp - 3}°F - Cloudy\n"
            f"  Day 4: {base_temp + 1}°F - Rainy\n"
            f"  Day 5: {base_temp}°F - Clear"
        )
    else:
        return f"Forecast data not available for {city}. Try: New York, London, Tokyo, Paris, or Sydney."


# Tool registry with ServerTool objects
TOOLS: dict[str, ServerTool] = {
    "get_weather": ServerTool(
        name="get_weather",
        title="Get Current Weather",
        description="Get current weather information for a specified city",
        input_schema={
            "type": "object",
            "required": ["city"],
            "properties": {
                "city": {
                    "type": "string",
                    "description": "Name of the city (e.g., 'New York', 'London', 'Tokyo')",
                }
            },
        },
        handler=get_weather_data
    ),
    "get_forecast": ServerTool(
        name="get_forecast",
        title="Get Weather Forecast",
        description="Get 5-day weather forecast for a specified city",
        input_schema={
            "type": "object",
            "required": ["city"],
            "properties": {
                "city": {
                    "type": "string",
                    "description": "Name of the city (e.g., 'New York', 'London', 'Tokyo')",
                }
            },
        },
        handler=get_forecast_data
    ),
}


@click.command()
@click.option("--port", default=8000, help="Port to listen on for SSE transport")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type (stdio or sse)",
)
def main(port:  int, transport: str) -> int:
    """Start the Weather MCP server."""
    app = Server("weather-server")
    
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
            async with stdio_server() as streams:
                await app.run(
                    streams[0], streams[1], app.create_initialization_options()
                )
        
        print("🌤️ Weather Server starting (STDIO transport)")
        anyio.run(run_stdio)
    
    return 0


if __name__ == "__main__": 
    main()