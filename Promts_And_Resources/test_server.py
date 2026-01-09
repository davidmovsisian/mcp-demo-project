#!/usr/bin/env python3
"""
Simple test for MCP server without OpenAI
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_server():
    """Test the MCP server basic functionality"""
    
    # Connect to MCP server
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            print("✓ Connected to MCP server\n")
            
            # Test 1: List prompts
            print("=== Test 1: List Prompts ===")
            prompts = await session.list_prompts()
            print(f"Found {len(prompts.prompts)} prompts:")
            for prompt in prompts.prompts:
                print(f"  - {prompt.name}: {prompt.description}")
            print()
            
            # Test 2: Get a prompt
            print("=== Test 2: Get Code Review Prompt ===")
            code_review = await session.get_prompt(
                name="code-review",
                arguments={
                    "file_path": "src/auth.py",
                    "focus_area": "security",
                },
            )
            prompt_text = code_review.messages[0].content.text
            print(f"Prompt length: {len(prompt_text)} characters")
            print(f"First 150 chars: {prompt_text[:150]}...\n")
            
            # Test 3: List resources
            print("=== Test 3: List Resources ===")
            resources = await session.list_resources()
            print(f"Found {len(resources.resources)} resources:")
            for resource in resources.resources:
                print(f"  - {resource.uri}: {resource.name}")
            print()
            
            # Test 4: Read a resource
            print("=== Test 4: Read Tasks Resource ===")
            tasks_resource = await session.read_resource(uri="project://tasks")
            print("Tasks content:")
            print(tasks_resource.contents[0].text)
            print()
            
            # Test 5: List tools
            print("=== Test 5: List Tools ===")
            tools = await session.list_tools()
            print(f"Found {len(tools.tools)} tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            print()
            
            # Test 6: Call a tool
            print("=== Test 6: Call update_task_status Tool ===")
            result = await session.call_tool(
                name="update_task_status",
                arguments={"task_id": 2, "status": "in-progress"},
            )
            print(f"Result: {result.content[0].text}")
            print()
            
            # Test 7: Call add_task tool
            print("=== Test 7: Call add_task Tool ===")
            result = await session.call_tool(
                name="add_task",
                arguments={
                    "title": "Test new feature",
                    "priority": "high",
                },
            )
            print(f"Result: {result.content[0].text}")
            print()
            
            # Test 8: Read summary resource
            print("=== Test 8: Read Project Summary ===")
            summary = await session.read_resource(uri="project://summary")
            print(summary.contents[0].text)
            
            print("\n✓ All tests passed!")


if __name__ == "__main__":
    asyncio.run(test_server())
