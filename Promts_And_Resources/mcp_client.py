#!/usr/bin/env python3
"""
MCP Client with OpenAI Integration
"""

import asyncio
import os
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI

# Validate OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Error: OPENAI_API_KEY environment variable is not set.", file=sys.stderr)
    print("Please set it with: export OPENAI_API_KEY='your-key-here'", file=sys.stderr)
    sys.exit(1)

# Initialize OpenAI client
openai_client = OpenAI(api_key=api_key)


async def main():
    """Run the MCP client with OpenAI integration"""
    
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
            print("=" * 60)
            
            # ============================================
            # EXAMPLE 1: Using Prompts
            # ============================================
            print("\n=== EXAMPLE 1: Using Prompts ===\n")
            
            # List available prompts
            prompts = await session.list_prompts()
            print("Available prompts:")
            for prompt in prompts.prompts:
                print(f"  - {prompt.name}: {prompt.description}")
            print()
            
            # Get a specific prompt with arguments
            code_review_prompt = await session.get_prompt(
                name="code-review",
                arguments={
                    "file_path": "src/auth.py",
                    "focus_area": "security",
                },
            )
            
            prompt_text = code_review_prompt.messages[0].content.text
            print("Code Review Prompt Generated:")
            print(prompt_text[:200] + "...\n")
            
            # Send prompt to OpenAI
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "user", "content": prompt_text}
                ],
                temperature=0.7,
            )
            
            print("OpenAI Response:")
            print(response.choices[0].message.content)
            print("\n" + "=" * 60 + "\n")
            
            # ============================================
            # EXAMPLE 2: Using Resources
            # ============================================
            print("=== EXAMPLE 2: Using Resources ===\n")
            
            # List available resources
            resources = await session.list_resources()
            print("Available resources:")
            for resource in resources.resources:
                print(f"  - {resource.uri}: {resource.name}")
            print()
            
            # Read a specific resource
            tasks_resource = await session.read_resource(uri="project://tasks")
            print("Tasks Resource Content:")
            print(tasks_resource.contents[0].text)
            print()
            
            # Read project summary
            summary_resource = await session.read_resource(uri="project://summary")
            print("Project Summary:")
            print(summary_resource.contents[0].text)
            print("\n" + "=" * 60 + "\n")
            
            # ============================================
            # EXAMPLE 3: Combining Resources with OpenAI
            # ============================================
            print("=== EXAMPLE 3: Resources + OpenAI Analysis ===\n")
            
            # Get sprint summary prompt with resource data
            sprint_prompt = await session.get_prompt(
                name="sprint-summary",
                arguments={"sprint_number": "5"},
            )
            
            sprint_prompt_text = sprint_prompt.messages[0].content.text
            
            # Send to OpenAI with resource context
            sprint_analysis = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a project management assistant analyzing sprint data.",
                    },
                    {"role": "user", "content": sprint_prompt_text},
                ],
                temperature=0.5,
            )
            
            print("Sprint Analysis:")
            print(sprint_analysis.choices[0].message.content)
            print("\n" + "=" * 60 + "\n")
            
            # ============================================
            # EXAMPLE 4: Using Tools
            # ============================================
            print("=== EXAMPLE 4: Using Tools ===\n")
            
            tools = await session.list_tools()
            print("Available tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            print()
            
            # Call a tool
            tool_result = await session.call_tool(
                name="update_task_status",
                arguments={"task_id": 2, "status": "in-progress"},
            )
            
            print("Tool Result:")
            print(tool_result.content[0].text)
            print()
            
            # Add a new task
            add_result = await session.call_tool(
                name="add_task",
                arguments={
                    "title": "Implement caching layer",
                    "priority": "high",
                },
            )
            
            print("Add Task Result:")
            print(add_result.content[0].text)
            print("\n" + "=" * 60 + "\n")
            
            # ============================================
            # EXAMPLE 5: Advanced - Multi-turn Conversation
            # ============================================
            print("=== EXAMPLE 5: Multi-turn with Context ===\n")
            
            # Get bug analysis prompt
            bug_prompt = await session.get_prompt(
                name="bug-analysis",
                arguments={
                    "bug_description": "Users cannot log in after deployment",
                    "error_logs": "TypeError: 'token' attribute not found",
                },
            )
            
            bug_prompt_text = bug_prompt.messages[0].content.text
            
            # Read relevant code resource
            auth_code = await session.read_resource(
                uri="project://codebase/src/auth.py"
            )
            
            # Create multi-turn conversation with OpenAI
            bug_analysis = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior software engineer debugging production issues.",
                    },
                    {"role": "user", "content": bug_prompt_text},
                    {
                        "role": "assistant",
                        "content": "I need to see the authentication code to provide accurate analysis.",
                    },
                    {
                        "role": "user",
                        "content": f"Here's the authentication module:\n\n{auth_code.contents[0].text}",
                    },
                ],
                temperature=0.3,
            )
            
            print("Bug Analysis with Code Context:")
            print(bug_analysis.choices[0].message.content)
            
            print("\n✓ Disconnected from MCP server")


if __name__ == "__main__":
    asyncio.run(main())
