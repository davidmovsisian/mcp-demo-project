"""
Test script for calculator server using SSE transport.
This allows debugging both client and server simultaneously.
"""
import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client
import mcp.types as types


async def test_calculator_server_sse():
    """Test the calculator server via SSE."""
    
    # Connect to running SSE server
    url = "http://localhost:8001/sse"
    
    print(f"🔌 Connecting to calculator server at {url}...")
    
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
                
                # Test add tool
                print("➕ Testing add: 5 + 3...")
                result = await session.call_tool("add", {"a": 5, "b": 3})
                for content in result.content:
                    if isinstance(content, types.TextContent):
                        print(content.text)
                print()
                
                # Test subtract tool
                print("➖ Testing subtract: 10 - 4...")
                result = await session.call_tool("subtract", {"a": 10, "b": 4})
                for content in result.content:
                    if isinstance(content, types.TextContent):
                        print(content.text)
                print()
                
                # Test multiply tool
                print("✖️  Testing multiply: 7 * 6...")
                result = await session.call_tool("multiply", {"a": 7, "b": 6})
                for content in result.content:
                    if isinstance(content, types.TextContent):
                        print(content.text)
                print()
                
                # Test divide tool
                print("➗ Testing divide: 20 / 4...")
                result = await session.call_tool("divide", {"a": 20, "b": 4})
                for content in result.content:
                    if isinstance(content, types.TextContent):
                        print(content.text)
                print()
                
                # Test divide by zero
                print("❗ Testing divide by zero: 10 / 0...")
                result = await session.call_tool("divide", {"a": 10, "b": 0})
                for content in result.content:
                    if isinstance(content, types.TextContent):
                        print(content.text)
                print()
                
                # Test with decimals
                print("🔢 Testing with decimals: 3.5 * 2.5...")
                result = await session.call_tool("multiply", {"a": 3.5, "b": 2.5})
                for content in result.content:
                    if isinstance(content, types.TextContent):
                        print(content.text)
                
                print("\n✅ All tests completed!")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Make sure the calculator server is running:")
        print("   Start it with: Debug Calculator Server (SSE) from the debug dropdown")


if __name__ == "__main__":
    asyncio.run(test_calculator_server_sse())
