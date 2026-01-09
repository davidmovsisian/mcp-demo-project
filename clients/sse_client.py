"""
Interactive SSE MCP Client. 
Connects to MCP servers via HTTP/SSE transport.
"""
import asyncio
import types
from typing import Optional
import click
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client
import mcp.types as types


async def run_interactive_session(server_url: str, server_name: str):
    """
    Run an interactive session with an MCP server via SSE.
    
    Args:
        server_url: Server URL (e.g., http://127.0.0.1:8000)
        server_name: Human-readable server name for display
    """
    print(f"\n🔌 Connecting to {server_name} at {server_url}...")
    
    try:
        async with sse_client(server_url) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize connection
                init_result = await session. initialize()
                print(f"✅ Connected to: {init_result.serverInfo.name}")
                print(f"   Protocol version: {init_result.protocolVersion}")
                
                # Get available tools
                tools_result = await session.list_tools()
                tools = {tool.name: tool for tool in tools_result.tools}
                
                if not tools:
                    print("⚠️  No tools available on this server")
                    return
                
                # Interactive loop
                while True:
                    print("\n" + "=" * 60)
                    print(f"📋 Available Tools on {server_name}:")
                    print("=" * 60)
                    
                    for i, (name, tool) in enumerate(tools.items(), 1):
                        print(f"{i}. {tool.name}")
                        print(f"   Title:  {tool.title}")
                        print(f"   Description: {tool.description}")
                        print(f"   Required params: {tool.inputSchema.get('required', [])}")
                        print()
                    
                    print("0. Exit")
                    print("=" * 60)
                    
                    # Get user choice
                    try:
                        choice = input("\nSelect a tool (number): ").strip()
                        
                        if choice == "0": 
                            print("👋 Goodbye!")
                            break
                        
                        tool_index = int(choice) - 1
                        if tool_index < 0 or tool_index >= len(tools):
                            print("❌ Invalid choice. Please try again.")
                            continue
                        
                        tool_name = list(tools.keys())[tool_index]
                        tool = tools[tool_name]
                        
                        # Get tool arguments from user
                        print(f"\n🔧 Calling tool: {tool.name}")
                        print(f"Required parameters: {tool.inputSchema. get('required', [])}")
                        
                        arguments = {}
                        properties = tool.inputSchema.get("properties", {})
                        required = tool.inputSchema.get("required", [])
                        
                        for param_name, param_info in properties.items():
                            param_type = param_info.get("type", "string")
                            param_desc = param_info. get("description", "")
                            is_required = param_name in required
                            
                            while True:
                                prompt = f"  {param_name}"
                                if param_desc: 
                                    prompt += f" ({param_desc})"
                                if is_required:
                                    prompt += " [required]"
                                prompt += ":  "
                                
                                value = input(prompt).strip()
                                
                                # Validate input
                                if not value and is_required:
                                    print(f"    ❌ {param_name} is required!")
                                    continue
                                
                                if not value: 
                                    break
                                
                                # Convert to appropriate type
                                try:
                                    if param_type == "number":
                                        value = float(value)
                                    elif param_type == "integer": 
                                        value = int(value)
                                    # string type needs no conversion
                                    
                                    arguments[param_name] = value
                                    break
                                except ValueError:
                                    print(f"    ❌ Invalid {param_type}. Please try again.")
                                    continue
                        
                        # Call the tool
                        print(f"\n⚙️  Executing {tool.name}...")
                        try:
                            result = await session.call_tool(tool_name, arguments)
                            
                            print("\n✅ Result:")
                            print("-" * 60)
                            for content in result.content:
                                if isinstance(content, types.TextContent):
                                    print(content.text)
                            print("-" * 60)
                        
                        except Exception as e: 
                            print(f"\n❌ Error: {e}")
                    
                    except ValueError:
                        print("❌ Invalid input. Please enter a number.")
                    except KeyboardInterrupt:
                        print("\n\n👋 Interrupted.  Goodbye!")
                        break
                    except EOFError: 
                        print("\n\n👋 EOF detected. Goodbye!")
                        break
    
    except Exception as e: 
        print(f"❌ Connection error: {e}")
        print(f"   Make sure the server is running at {server_url}")
        return 1


@click.command()
@click.option(
    "--url",
    default="http://127.0.0.1:8000",
    help="Server URL (default: http://127.0.0.1:8000 for weather server)",
)
@click.option(
    "--server",
    type=click.Choice(["weather", "calculator"]),
    default="weather",
    help="Which server to connect to (sets default URL)",
)
def main(url: str, server: str):
    """
    Interactive SSE MCP Client.
    
    Connects to an MCP server via SSE transport (HTTP) and provides
    an interactive menu for calling tools.
    
    The server must already be running! 
    
    Examples:
    
        # Connect to weather server (default port 8000)
        sse-client --server weather
        
        # Connect to calculator server (default port 8001)
        sse-client --server calculator
        
        # Connect to custom URL
        sse-client --url http://localhost:9000
    """
    # Override URL based on server choice if using default
    if url == "http://127.0.0.1:8000":  # Using default
        if server == "calculator":
            url = "http://127.0.0.1:8001"
    
    server_name = f"{server. title()} Server"
    
    print("=" * 60)
    print("🚀 Interactive SSE MCP Client")
    print("=" * 60)
    print(f"⚠️  Make sure the server is running:")
    if server == "weather":
        print(f"   uv run mcp-weather --transport sse --port 8000")
    else:
        print(f"   uv run mcp-calculator --transport sse --port 8001")
    
    try:
        asyncio.run(run_interactive_session(url, server_name))
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__": 
    main()