"""
Quick test script for weather server.
"""
import asyncio
from mcp.client. session import ClientSession
from mcp.client. stdio import StdioServerParameters, stdio_client
import mcp.types as types

async def test_weather_server():
    """Test the weather server."""
    
    # Configure server to start
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "mcp-weather"]
    )
    
    print("🔌 Connecting to weather server...")
    
    # Connect to server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()
            print("✅ Connected!\n")
            
            # List available tools
            print("📋 Available tools:")
            tools = await session.list_tools()
            for tool in tools. tools:
                print(f"  - {tool.name}:  {tool.description}")
            print()
            
            # Test get_weather tool
            print("🌤️  Testing get_weather for 'New York'...")
            result = await session.call_tool("get_weather", {"city": "New York"})
            for content in result. content:
                if isinstance(content, types.TextContent):
                    print(content.text)
            print()
            
            # Test get_weather for another city
            print("🌤️  Testing get_weather for 'Tokyo'...")
            result = await session.call_tool("get_weather", {"city": "Tokyo"})
            for content in result.content:
                if isinstance(content, types.TextContent):
                    print(content.text)
            print()
            
            # Test get_forecast tool
            print("📅 Testing get_forecast for 'London'...")
            result = await session.call_tool("get_forecast", {"city": "London"})
            for content in result.content:
                if isinstance(content, types.TextContent):
                    print(content.text)
            print()
            
            # Test with unknown city
            print("❓ Testing with unknown city 'Mars'...")
            result = await session.call_tool("get_weather", {"city": "Mars"})
            for content in result.content:
                if isinstance(content, types.TextContent):
                    print(content.text)
            
            print("\n✅ All tests completed!")


if __name__ == "__main__":
    asyncio. run(test_weather_server())