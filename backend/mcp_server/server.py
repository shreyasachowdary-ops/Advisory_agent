"""MCP stdio server exposing advisor tools."""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Ensure backend root is on path when run as subprocess
BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from mcp_server.tools.activity_plan import create_activity_plan
from mcp_server.tools.safeguarding import submit_safeguarding_flag
from mcp_server.tools.school_policy import get_school_policy
from mcp_server.tools.search_knowledge import search_knowledge

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_server")

SCHEMAS_DIR = Path(__file__).parent / "schemas"

server = Server("advisor-tools")


def _load_schema(name: str) -> dict:
    with open(SCHEMAS_DIR / f"{name}.json", encoding="utf-8") as f:
        return json.load(f)


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_knowledge",
            description="Read-only vector retrieval from curated early-childhood knowledge base.",
            inputSchema=_load_schema("search_knowledge"),
        ),
        Tool(
            name="create_activity_plan",
            description="Generate a deterministic, editable, play-based activity plan.",
            inputSchema=_load_schema("create_activity_plan"),
        ),
        Tool(
            name="get_school_policy",
            description="Read-only lookup of school policy from mock data.",
            inputSchema=_load_schema("get_school_policy"),
        ),
        Tool(
            name="submit_safeguarding_flag",
            description=(
                "Submit a safeguarding concern to the test audit log. "
                "Requires user_confirmed=true. PoC test sink only."
            ),
            inputSchema=_load_schema("submit_safeguarding_flag"),
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        if name == "search_knowledge":
            result = search_knowledge(**arguments)
        elif name == "create_activity_plan":
            result = create_activity_plan(**arguments)
        elif name == "get_school_policy":
            result = get_school_policy(**arguments)
        elif name == "submit_safeguarding_flag":
            result = submit_safeguarding_flag(**arguments)
        else:
            result = {"error": f"Unknown tool: {name}"}
    except Exception as exc:
        logger.exception("Tool %s failed", name)
        result = {"error": str(exc)}

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
