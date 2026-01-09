#!/usr/bin/env python3
"""
MCP Server implementing Prompts, Resources, and Tools
"""

import asyncio
import json
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Prompt,
    PromptArgument,
    PromptMessage,
    TextContent,
    Resource,
    Tool,
    GetPromptResult,
    CallToolResult,
)

# Sample data store
PROJECT_DATA = {
    "tasks": [
        {"id": 1, "title": "Implement authentication", "status": "in-progress", "priority": "high"},
        {"id": 2, "title": "Write documentation", "status": "todo", "priority": "medium"},
        {"id": 3, "title": "Fix bug #123", "status": "completed", "priority": "high"},
    ],
    "codebase": {
        "src/auth.py": """# Authentication module
def authenticate(user: str) -> bool:
    '''Authenticate a user'''
    return True
    
def get_token(user: str) -> str:
    '''Generate authentication token'''
    return f"token_{user}"
""",
        "src/api.py": """# API endpoints
ENDPOINTS = ['/users', '/tasks', '/auth']

def get_endpoint(name: str):
    '''Get API endpoint by name'''
    return f"/api/v1{name}"
""",
    },
}

# Create server instance
app = Server("project-assistant")


# ============================================
# PROMPTS IMPLEMENTATION
# ============================================

@app.list_prompts()
async def list_prompts() -> list[Prompt]:
    """List available prompts"""
    return [
        Prompt(
            name="code-review",
            description="Generate a comprehensive code review for a file",
            arguments=[
                PromptArgument(
                    name="file_path",
                    description="Path to the file to review",
                    required=True,
                ),
                PromptArgument(
                    name="focus_area",
                    description="Specific area to focus on (security, performance, style)",
                    required=False,
                ),
            ],
        ),
        Prompt(
            name="sprint-summary",
            description="Create a sprint summary with tasks and progress",
            arguments=[
                PromptArgument(
                    name="sprint_number",
                    description="Sprint number",
                    required=True,
                ),
            ],
        ),
        Prompt(
            name="bug-analysis",
            description="Analyze a bug and suggest fixes",
            arguments=[
                PromptArgument(
                    name="bug_description",
                    description="Description of the bug",
                    required=True,
                ),
                PromptArgument(
                    name="error_logs",
                    description="Error logs if available",
                    required=False,
                ),
            ],
        ),
    ]


@app.get_prompt()
async def get_prompt(name: str, arguments: dict[str, str] | None) -> GetPromptResult:
    """Get a specific prompt with arguments"""
    
    if name == "code-review":
        file_path = arguments.get("file_path", "") if arguments else ""
        focus_area = arguments.get("focus_area", "general") if arguments else "general"
        file_content = PROJECT_DATA["codebase"].get(file_path, "File not found")
        
        prompt_text = f"""Please perform a {focus_area} code review for the following file:

File: {file_path}

```
{file_content}
```

Focus areas: 
- Code quality and best practices
- Potential bugs or issues
- Performance considerations
- Security concerns
{f"\\nPay special attention to: {focus_area}" if focus_area != "general" else ""}

Provide actionable feedback and suggestions."""

        return GetPromptResult(
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=prompt_text,
                    ),
                )
            ]
        )
    
    elif name == "sprint-summary":
        sprint_number = arguments.get("sprint_number", "N/A") if arguments else "N/A"
        tasks = PROJECT_DATA["tasks"]
        
        tasks_summary = "\n".join(
            f"- [{t['status']}] {t['title']} (Priority: {t['priority']})"
            for t in tasks
        )
        
        prompt_text = f"""Generate a comprehensive sprint {sprint_number} summary: 

**Current Tasks:**
{tasks_summary}

**Instructions:**
1. Summarize the overall progress
2. Highlight completed items
3. Identify blockers or risks
4. Suggest priorities for next sprint
5. Calculate completion percentage

Format the summary in a clear, executive-friendly format."""

        return GetPromptResult(
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=prompt_text,
                    ),
                )
            ]
        )
    
    elif name == "bug-analysis":
        bug_description = arguments.get("bug_description", "No description") if arguments else "No description"
        error_logs = arguments.get("error_logs", "No logs provided") if arguments else "No logs provided"
        
        prompt_text = f"""Analyze this bug and provide a detailed solution:

**Bug Description:**
{bug_description}

**Error Logs:**
```
{error_logs}
```

**Analysis Required:**
1. Root cause analysis
2. Potential fixes (at least 3 options)
3. Impact assessment
4. Testing strategy
5. Prevention measures for future

**Context:** This is a {len(PROJECT_DATA['tasks'])}-task project with authentication and API modules."""

        return GetPromptResult(
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=prompt_text,
                    ),
                )
            ]
        )
    
    raise ValueError(f"Unknown prompt: {name}")


# ============================================
# RESOURCES IMPLEMENTATION
# ============================================

@app.list_resources()
async def list_resources() -> list[Resource]:
    """List available resources"""
    return [
        Resource(
            uri="project://tasks",
            name="Project Tasks",
            description="Current project tasks with status and priority",
            mimeType="application/json",
        ),
        Resource(
            uri="project://codebase/src/auth.py",
            name="Authentication Module",
            description="Source code for authentication",
            mimeType="text/plain",
        ),
        Resource(
            uri="project://codebase/src/api.py",
            name="API Module",
            description="API endpoints definition",
            mimeType="text/plain",
        ),
        Resource(
            uri="project://summary",
            name="Project Summary",
            description="Overall project status and metrics",
            mimeType="text/markdown",
        ),
    ]


@app.read_resource()
async def read_resource(uri: str) -> str:
    """Read a specific resource"""
    # Convert URI to string (it may come as AnyUrl type)
    uri_str = str(uri)
    
    if uri_str == "project://tasks":
        return json.dumps(PROJECT_DATA["tasks"], indent=2)
    
    elif uri_str == "project://codebase/src/auth.py":
        return PROJECT_DATA["codebase"]["src/auth.py"]
    
    elif uri_str == "project://codebase/src/api.py":
        return PROJECT_DATA["codebase"]["src/api.py"]
    
    elif uri_str == "project://summary":
        tasks = PROJECT_DATA["tasks"]
        completed = sum(1 for t in tasks if t["status"] == "completed")
        total = len(tasks)
        percentage = (completed / total * 100) if total > 0 else 0
        
        in_progress = sum(1 for t in tasks if t["status"] == "in-progress")
        todo = sum(1 for t in tasks if t["status"] == "todo")
        
        high_priority = [t for t in tasks if t["priority"] == "high"]
        high_priority_items = "\n".join(
            f"- [{t['status']}] {t['title']}" for t in high_priority
        )
        
        summary = f"""# Project Status Summary

## Overview
- **Total Tasks:** {total}
- **Completed:** {completed}
- **In Progress:** {in_progress}
- **Todo:** {todo}
- **Completion Rate:** {percentage:.1f}%

## High Priority Items
{high_priority_items}

## Code Modules
- Authentication (auth.py)
- API Endpoints (api.py)
"""
        
        return summary
    
    raise ValueError(f"Resource not found: {uri_str}")


# ============================================
# TOOLS (Bonus - for completeness)
# ============================================

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="update_task_status",
            description="Update the status of a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "number",
                        "description": "ID of the task to update",
                    },
                    "status": {
                        "type": "string",
                        "enum": ["todo", "in-progress", "completed"],
                        "description": "New status",
                    },
                },
                "required": ["task_id", "status"],
            },
        ),
        Tool(
            name="add_task",
            description="Add a new task to the project",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Task title",
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Task priority",
                    },
                },
                "required": ["title", "priority"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> CallToolResult:
    """Execute a tool"""
    
    if name == "update_task_status":
        task_id = arguments.get("task_id")
        status = arguments.get("status")
        
        task = next((t for t in PROJECT_DATA["tasks"] if t["id"] == task_id), None)
        
        if not task:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Task {task_id} not found",
                    )
                ],
                isError=True,
            )
        
        task["status"] = status
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Updated task {task_id} \"{task['title']}\" to status: {status}",
                )
            ]
        )
    
    elif name == "add_task":
        title = arguments.get("title")
        priority = arguments.get("priority", "medium")
        
        new_id = max(t["id"] for t in PROJECT_DATA["tasks"]) + 1
        new_task = {
            "id": new_id,
            "title": title,
            "status": "todo",
            "priority": priority,
        }
        
        PROJECT_DATA["tasks"].append(new_task)
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Added new task {new_id}: \"{title}\" (Priority: {priority})",
                )
            ]
        )
    
    raise ValueError(f"Unknown tool: {name}")


# ============================================
# START SERVER
# ============================================

async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
