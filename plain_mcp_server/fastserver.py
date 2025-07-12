"""FastMCP Server implementation for Plain.com API"""

import json
import logging
import os
from typing import Any

import httpx
from mcp.server import FastMCP
from pydantic import BaseModel, Field

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
    workspace_id: str | None = Field(default=None, description="Workspace ID (if required)")


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
        self, query: str, variables: dict[str, Any] | None = None
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


# Initialize the FastMCP server
mcp_server = FastMCP("plain-mcp-server")

# Global client instance
plain_client: PlainClient | None = None


async def get_client() -> PlainClient:
    """Get or create the Plain.com client"""
    global plain_client
    if plain_client is None:
        api_key = os.getenv("PLAIN_API_KEY")
        if not api_key:
            raise ValueError("PLAIN_API_KEY environment variable is required")

        config = PlainConfig(api_key=api_key)
        plain_client = PlainClient(config)
        logger.info("Plain.com client initialized successfully")

    return plain_client


@mcp_server.tool()
async def fetch_threads(
    status: str | None = None,
    assignee_id: str | None = None,
    customer_id: str | None = None,
    limit: int = 10,
    include_resolved: bool = False,
) -> str:
    """
    Fetch support threads (tickets) with optional filters.

    Args:
        status: Filter by thread status (TODO, DONE, SNOOZED)
        assignee_id: Filter by assigned user ID
        customer_id: Filter by customer ID
        limit: Maximum number of threads to return
        include_resolved: Include resolved/done threads

    Returns:
        JSON string with threads data
    """
    client = await get_client()

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

    data = await client.execute_query(query)
    result = {
        "threads": [edge["node"] for edge in data.get("threads", {}).get("edges", [])],
        "hasMore": data.get("threads", {}).get("pageInfo", {}).get("hasNextPage", False),
    }
    return json.dumps(result, indent=2)


@mcp_server.tool()
async def search_threads(query: str, limit: int = 10) -> str:
    """
    Search through support threads using text search.

    Args:
        query: Search query for thread content
        limit: Maximum number of results

    Returns:
        JSON string with search results
    """
    client = await get_client()

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

    data = await client.execute_query(search_query)
    result = {
        "results": [
            edge["node"]["thread"] for edge in data.get("searchThreads", {}).get("edges", [])
        ]
    }
    return json.dumps(result, indent=2)


@mcp_server.tool()
async def get_thread_details(thread_id: str) -> str:
    """
    Get detailed information about a specific thread including timeline.

    Args:
        thread_id: Thread ID to get details for

    Returns:
        JSON string with thread details
    """
    client = await get_client()

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

    data = await client.execute_query(query)
    result = data.get("thread", {})
    return json.dumps(result, indent=2)


@mcp_server.tool()
async def update_thread_status(thread_id: str, status: str) -> str:
    """
    Update the status of a support thread.

    Args:
        thread_id: Thread ID to update
        status: New status (TODO, DONE, SNOOZED)

    Returns:
        JSON string with update result
    """
    client = await get_client()

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

    data = await client.execute_query(mutation)
    result = data.get("updateThread", {})
    return json.dumps(result, indent=2)


@mcp_server.tool()
async def add_thread_note(thread_id: str, content: str) -> str:
    """
    Add a note to a support thread.

    Args:
        thread_id: Thread ID to add note to
        content: Note content

    Returns:
        JSON string with note creation result
    """
    client = await get_client()

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

    data = await client.execute_query(mutation)
    result = data.get("createThreadNote", {})
    return json.dumps(result, indent=2)


@mcp_server.tool()
async def get_customer_info(customer_id: str) -> str:
    """
    Get detailed information about a customer.

    Args:
        customer_id: Customer ID to get info for

    Returns:
        JSON string with customer information
    """
    client = await get_client()

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

    data = await client.execute_query(query)
    result = data.get("customer", {})
    return json.dumps(result, indent=2)


@mcp_server.tool()
async def analyze_thread_patterns(thread_id: str, days_back: int = 30) -> str:
    """
    Analyze patterns in threads to find similar issues.

    Args:
        thread_id: Reference thread ID to find similar issues
        days_back: Number of days to look back

    Returns:
        JSON string with pattern analysis
    """
    # First get the reference thread
    thread_details_data = await get_thread_details(thread_id)
    thread_details = json.loads(thread_details_data)

    if not thread_details:
        return json.dumps({"error": "Thread not found"}, indent=2)

    # Extract keywords from title and description for similarity search
    title = thread_details.get("title", "")
    description = thread_details.get("description", "")

    # Search for similar threads
    search_terms = f"{title} {description}"
    similar_threads_data = await search_threads(search_terms, limit=10)
    similar_threads = json.loads(similar_threads_data)

    # Filter out the original thread and add analysis
    filtered_results = []
    for thread in similar_threads.get("results", []):
        if thread.get("id") != thread_id:
            filtered_results.append(thread)

    result = {
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
    return json.dumps(result, indent=2)


def main():
    """Main entry point"""
    logger.info("Starting Plain.com MCP Server...")

    # Start the server
    mcp_server.run("stdio")


if __name__ == "__main__":
    main()
