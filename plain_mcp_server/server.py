"""Plain.com MCP Server

This module implements the MCP server for Plain.com customer support operations.
It provides tools for AI assistants to manage support tickets, search data, and
automate customer support workflows.
"""

import asyncio
import json
import logging
import os
from typing import Any, Optional

import httpx
from dotenv import load_dotenv
from mcp.server import Server
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    TextContent,
    Tool,
)
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlainConfig(BaseModel):
    """Configuration for Plain.com API"""

    api_key: str = Field(..., description="Plain.com API key")
    base_url: str = Field(
        default="https://core-api.uk.plain.com/graphql/v1",
        description="Plain.com GraphQL endpoint",
    )
    workspace_id: Optional[str] = Field(default=None, description="Workspace ID (if required)")


class PlainClient:
    """Client for Plain.com GraphQL API"""

    def __init__(self, config: PlainConfig):
        self.config = config
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    async def execute_query(
        self, query: str, variables: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Execute a GraphQL query"""
        payload = {
            "query": query,
            "variables": variables or {},
        }

        try:
            response = await self.client.post(self.config.base_url, json=payload)
            response.raise_for_status()
            data = response.json()

            if "errors" in data:
                error_messages = [error.get("message", str(error)) for error in data["errors"]]
                raise Exception(f"GraphQL errors: {'; '.join(error_messages)}")

            return data.get("data", {})
        except httpx.HTTPError as e:
            logger.error(f"HTTP error executing query: {e}")
            raise Exception(f"HTTP error: {e}")
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


class PlainMCPServer:
    """MCP Server for Plain.com operations"""

    def __init__(self):
        self.server = Server("plain-mcp-server")
        self.client: Optional[PlainClient] = None
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup MCP server handlers"""

        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """List available tools"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="fetch_threads",
                        description="Fetch support threads (tickets) with optional filters",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "status": {
                                    "type": "string",
                                    "enum": ["TODO", "DONE", "SNOOZED"],
                                    "description": "Filter by thread status",
                                },
                                "assignee_id": {
                                    "type": "string",
                                    "description": "Filter by assigned user ID",
                                },
                                "customer_id": {
                                    "type": "string",
                                    "description": "Filter by customer ID",
                                },
                                "limit": {
                                    "type": "integer",
                                    "default": 10,
                                    "description": "Maximum number of threads to return",
                                },
                                "include_resolved": {
                                    "type": "boolean",
                                    "default": False,
                                    "description": "Include resolved/done threads",
                                },
                            },
                        },
                    ),
                    Tool(
                        name="search_threads",
                        description="Search through support threads using text search",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Search query for thread content",
                                },
                                "limit": {
                                    "type": "integer",
                                    "default": 10,
                                    "description": "Maximum number of results",
                                },
                            },
                            "required": ["query"],
                        },
                    ),
                    Tool(
                        name="get_thread_details",
                        description=(
                            "Get detailed information about a specific thread " "including timeline"
                        ),
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "thread_id": {
                                    "type": "string",
                                    "description": "Thread ID to get details for",
                                }
                            },
                            "required": ["thread_id"],
                        },
                    ),
                    Tool(
                        name="update_thread_status",
                        description="Update the status of a support thread",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "thread_id": {
                                    "type": "string",
                                    "description": "Thread ID to update",
                                },
                                "status": {
                                    "type": "string",
                                    "enum": ["TODO", "DONE", "SNOOZED"],
                                    "description": "New status for the thread",
                                },
                            },
                            "required": ["thread_id", "status"],
                        },
                    ),
                    Tool(
                        name="add_thread_note",
                        description="Add a note to a support thread",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "thread_id": {
                                    "type": "string",
                                    "description": "Thread ID to add note to",
                                },
                                "content": {
                                    "type": "string",
                                    "description": "Note content",
                                },
                            },
                            "required": ["thread_id", "content"],
                        },
                    ),
                    Tool(
                        name="get_customer_info",
                        description="Get detailed information about a customer",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "customer_id": {
                                    "type": "string",
                                    "description": "Customer ID to get info for",
                                }
                            },
                            "required": ["customer_id"],
                        },
                    ),
                    Tool(
                        name="analyze_thread_patterns",
                        description="Analyze patterns in threads to find similar issues",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "thread_id": {
                                    "type": "string",
                                    "description": "Reference thread ID to find similar issues",
                                },
                                "days_back": {
                                    "type": "integer",
                                    "default": 30,
                                    "description": "Number of days to look back",
                                },
                            },
                            "required": ["thread_id"],
                        },
                    ),
                ]
            )

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> CallToolResult:
            """Handle tool calls"""
            if not self.client:
                return CallToolResult(
                    content=[
                        TextContent(type="text", text="Error: Plain.com client not initialized")
                    ]
                )

            try:
                if name == "fetch_threads":
                    result = await self._fetch_threads(**arguments)
                elif name == "search_threads":
                    result = await self._search_threads(**arguments)
                elif name == "get_thread_details":
                    result = await self._get_thread_details(**arguments)
                elif name == "update_thread_status":
                    result = await self._update_thread_status(**arguments)
                elif name == "add_thread_note":
                    result = await self._add_thread_note(**arguments)
                elif name == "get_customer_info":
                    result = await self._get_customer_info(**arguments)
                elif name == "analyze_thread_patterns":
                    result = await self._analyze_thread_patterns(**arguments)
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"Unknown tool: {name}")]
                    )

                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps(result, indent=2))]
                )
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}")
                return CallToolResult(content=[TextContent(type="text", text=f"Error: {str(e)}")])

    async def _fetch_threads(
        self,
        status: Optional[str] = None,
        assignee_id: Optional[str] = None,
        customer_id: Optional[str] = None,
        limit: int = 10,
        include_resolved: bool = False,
    ) -> dict[str, Any]:
        """Fetch support threads with filters"""

        # Build filter conditions
        filters = []
        if status:
            filters.append(f"status: {status}")
        if assignee_id:
            filters.append(f'assignedToUser: {{userId: "{assignee_id}"}}')
        if customer_id:
            filters.append(f'customerId: "{customer_id}"')
        if not include_resolved:
            filters.append("status: {isIn: [TODO, SNOOZED]}")

        filters_str = ", ".join(filters)
        if filters_str:
            filters_str = f"filters: {{{filters_str}}}"

        query = f"""
        query GetThreads {{
            threads({filters_str}, first: {limit}) {{
                edges {{
                    node {{
                        id
                        title
                        description
                        status
                        statusChangedAt
                        assignedToUser {{
                            id
                            fullName
                        }}
                        customer {{
                            id
                            fullName
                            email {{
                                email
                            }}
                        }}
                        createdAt
                        updatedAt
                        priority
                        labels {{
                            id
                            labelType {{
                                name
                            }}
                        }}
                    }}
                }}
                pageInfo {{
                    hasNextPage
                    endCursor
                }}
            }}
        }}
        """

        if not self.client:
            raise ValueError("Plain.com client not initialized")

        data = await self.client.execute_query(query)
        return {
            "threads": [edge["node"] for edge in data.get("threads", {}).get("edges", [])],
            "hasMore": data.get("threads", {}).get("pageInfo", {}).get("hasNextPage", False),
        }

    async def _search_threads(self, query: str, limit: int = 10) -> dict[str, Any]:
        """Search through support threads"""

        search_query = f"""
        query SearchThreads {{
            searchThreads(searchQuery: {{
                term: "{query}"
            }}, first: {limit}) {{
                edges {{
                    node {{
                        thread {{
                            id
                            title
                            description
                            status
                            customer {{
                                id
                                fullName
                                email {{
                                    email
                                }}
                            }}
                            createdAt
                            updatedAt
                        }}
                    }}
                }}
            }}
        }}
        """

        if not self.client:
            raise ValueError("Plain.com client not initialized")

        data = await self.client.execute_query(search_query)
        return {
            "results": [
                edge["node"]["thread"] for edge in data.get("searchThreads", {}).get("edges", [])
            ]
        }

    async def _get_thread_details(self, thread_id: str) -> dict[str, Any]:
        """Get detailed thread information"""

        query = f"""
        query GetThreadDetails {{
            thread(threadId: "{thread_id}") {{
                id
                title
                description
                status
                statusChangedAt
                assignedToUser {{
                    id
                    fullName
                }}
                customer {{
                    id
                    fullName
                    email {{
                        email
                    }}
                    company {{
                        id
                        name
                    }}
                }}
                createdAt
                updatedAt
                priority
                labels {{
                    id
                    labelType {{
                        name
                    }}
                }}
                timeline(first: 20) {{
                    edges {{
                        node {{
                            id
                            timestamp
                            actor {{
                                ... on UserActor {{
                                    user {{
                                        id
                                        fullName
                                    }}
                                }}
                                ... on CustomerActor {{
                                    customer {{
                                        id
                                        fullName
                                    }}
                                }}
                            }}
                            ... on ThreadChatTimelineEntry {{
                                chat {{
                                    text
                                }}
                            }}
                            ... on ThreadNoteTimelineEntry {{
                                note {{
                                    text
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
        """

        if not self.client:
            raise ValueError("Plain.com client not initialized")

        data = await self.client.execute_query(query)
        return data.get("thread", {})

    async def _update_thread_status(self, thread_id: str, status: str) -> dict[str, Any]:
        """Update thread status"""

        if not self.client:
            raise ValueError("Plain.com client not initialized")

        mutation = f"""
        mutation UpdateThreadStatus {{
            updateThread(input: {{
                threadId: "{thread_id}"
                status: {status}
            }}) {{
                thread {{
                    id
                    status
                    statusChangedAt
                }}
                error {{
                    message
                    code
                }}
            }}
        }}
        """

        data = await self.client.execute_query(mutation)
        return data.get("updateThread", {})

    async def _add_thread_note(self, thread_id: str, content: str) -> dict[str, Any]:
        """Add a note to a thread"""

        if not self.client:
            raise ValueError("Plain.com client not initialized")

        mutation = f"""
        mutation AddThreadNote {{
            createThreadNote(input: {{
                threadId: "{thread_id}"
                text: "{content}"
            }}) {{
                threadNote {{
                    id
                    text
                    createdAt
                }}
                error {{
                    message
                    code
                }}
            }}
        }}
        """

        data = await self.client.execute_query(mutation)
        return data.get("createThreadNote", {})

    async def _get_customer_info(self, customer_id: str) -> dict[str, Any]:
        """Get customer information"""

        if not self.client:
            raise ValueError("Plain.com client not initialized")

        query = f"""
        query GetCustomer {{
            customer(customerId: "{customer_id}") {{
                id
                fullName
                email {{
                    email
                    isVerified
                }}
                company {{
                    id
                    name
                    domainName
                }}
                createdAt
                updatedAt
                tenantMemberships(first: 5) {{
                    edges {{
                        node {{
                            tenant {{
                                id
                                name
                            }}
                        }}
                    }}
                }}
            }}
        }}
        """

        data = await self.client.execute_query(query)
        return data.get("customer", {})

    async def _analyze_thread_patterns(self, thread_id: str, days_back: int = 30) -> dict[str, Any]:
        """Analyze patterns to find similar threads"""

        # First get the reference thread
        thread_details = await self._get_thread_details(thread_id)

        if not thread_details:
            return {"error": "Thread not found"}

        # Extract keywords from title and description for similarity search
        title = thread_details.get("title", "")
        description = thread_details.get("description", "")

        # Search for similar threads
        search_terms = f"{title} {description}"
        similar_threads = await self._search_threads(search_terms, limit=10)

        # Filter out the original thread and add analysis
        filtered_results = []
        for thread in similar_threads.get("results", []):
            if thread.get("id") != thread_id:
                filtered_results.append(thread)

        return {
            "reference_thread": {
                "id": thread_details.get("id"),
                "title": thread_details.get("title"),
                "status": thread_details.get("status"),
            },
            "similar_threads": filtered_results[:5],  # Top 5 similar threads
            "analysis": {
                "total_found": len(filtered_results),
                "search_terms": search_terms,
            },
        }

    async def initialize(self):
        """Initialize the Plain.com client"""
        api_key = os.getenv("PLAIN_API_KEY")
        if not api_key:
            raise ValueError("PLAIN_API_KEY environment variable is required")

        config = PlainConfig(api_key=api_key)
        self.client = PlainClient(config)
        logger.info("Plain.com MCP server initialized successfully")

    async def run(self):
        """Run the MCP server"""
        await self.initialize()

        # Import and run the server
        from mcp.server.stdio import stdio_server

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream)


async def main():
    """Main entry point"""
    server = PlainMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
