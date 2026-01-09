"""
Test script for weather server using SSE transport.
This allows debugging both client and server simultaneously.
"""
import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client
import mcp.types as types


async def test_weather_server_sse():
    """Test the weather server via SSE."""
    
    # Connect to running SSE server
    url = "http://localhost:8000/sse"
    
    print(f"🔌 Connecting to weather server at {url}...")
    
    try:
        async with sse_client(url) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize
                await session.initialize()
                print("✅ Connected!\n")
                
                # List available tools
                print("📋 Available tools:")
                tools = await session.list_tools()
                for tool in tools.tools:
                    print(f"  - {tool.name}: {tool.description}")
                print()
                
                # Test get_weather tool
                print("🌤️  Testing get_weather for 'New York'...")
                result = await session.call_tool("get_weather", {"city": "New York"})
                for content in result.content:
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
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Make sure the weather server is running:")
        print("   Start it with: Debug Weather Server (SSE) from the debug dropdown")


if __name__ == "__main__":
    asyncio.run(test_weather_server_sse())
