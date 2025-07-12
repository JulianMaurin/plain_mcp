"""Test configuration and fixtures for Plain.com MCP Server"""

import os
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from plain_mcp_server.server import PlainClient, PlainConfig, PlainMCPServer


@pytest.fixture
def mock_config():
    """Mock Plain.com configuration"""
    return PlainConfig(
        api_key="test_api_key_123",
        base_url="https://test.plain.com/graphql",
        workspace_id="test_workspace_123",
    )


@pytest.fixture
def mock_thread_data():
    """Mock thread data for testing"""
    return {
        "id": "th_test123",
        "title": "Test Support Ticket",
        "description": "This is a test support ticket",
        "status": "TODO",
        "statusChangedAt": "2024-01-01T10:00:00Z",
        "assignedToUser": {"id": "user_123", "fullName": "Test User"},
        "customer": {
            "id": "cust_456",
            "fullName": "Test Customer",
            "email": {"email": "test@example.com"},
        },
        "createdAt": "2024-01-01T09:00:00Z",
        "updatedAt": "2024-01-01T10:00:00Z",
        "priority": "MEDIUM",
        "labels": [{"id": "label_789", "labelType": {"name": "Bug"}}],
    }


@pytest.fixture
def mock_customer_data():
    """Mock customer data for testing"""
    return {
        "id": "cust_test456",
        "fullName": "Test Customer",
        "email": {"email": "customer@example.com", "isVerified": True},
        "company": {
            "id": "comp_789",
            "name": "Test Company",
            "domainName": "example.com",
        },
        "createdAt": "2024-01-01T08:00:00Z",
        "updatedAt": "2024-01-01T09:00:00Z",
        "tenantMemberships": {
            "edges": [{"node": {"tenant": {"id": "tenant_111", "name": "Test Tenant"}}}]
        },
    }


@pytest.fixture
def mock_search_results(mock_thread_data):
    """Mock search results for testing"""
    return {"searchThreads": {"edges": [{"node": {"thread": mock_thread_data}}]}}


@pytest.fixture
def mock_thread_timeline():
    """Mock thread timeline data"""
    return {
        "edges": [
            {
                "node": {
                    "id": "timeline_1",
                    "timestamp": "2024-01-01T09:30:00Z",
                    "actor": {"user": {"id": "user_123", "fullName": "Test User"}},
                    "chat": {"text": "Hello, I need help with my account"},
                }
            },
            {
                "node": {
                    "id": "timeline_2",
                    "timestamp": "2024-01-01T09:45:00Z",
                    "actor": {"user": {"id": "user_123", "fullName": "Test User"}},
                    "note": {"text": "Customer contacted via email"},
                }
            },
        ]
    }


@pytest.fixture
def mock_httpx_client():
    """Mock httpx client for testing"""
    mock_client = AsyncMock(spec=httpx.AsyncClient)

    # Mock successful response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "data": {
            "threads": {
                "edges": [],
                "pageInfo": {"hasNextPage": False, "endCursor": None},
            }
        }
    }

    mock_client.post.return_value = mock_response
    return mock_client


@pytest.fixture
async def mock_plain_client(mock_config, mock_httpx_client):
    """Mock PlainClient for testing"""
    client = PlainClient(mock_config)
    client.client = mock_httpx_client
    return client


@pytest.fixture
async def mock_plain_server():
    """Mock PlainMCPServer for testing"""
    server = PlainMCPServer()
    # Mock the client initialization
    server.client = AsyncMock()
    return server


@pytest.fixture
def mock_env_vars():
    """Mock environment variables"""
    original_env = dict(os.environ)
    os.environ["PLAIN_API_KEY"] = "test_api_key_123"
    os.environ["PLAIN_WORKSPACE_ID"] = "test_workspace_123"

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_graphql_response():
    """Mock GraphQL response factory"""

    def _create_response(data: dict[str, Any], errors: list = None):
        response = {"data": data}
        if errors:
            response["errors"] = errors
        return response

    return _create_response


@pytest.fixture
def mock_mcp_tool_request():
    """Mock MCP tool request"""
    return {
        "method": "tools/call",
        "params": {
            "name": "fetch_threads",
            "arguments": {"status": "TODO", "limit": 10},
        },
    }


class MockResponse:
    """Mock HTTP response class"""

    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")


@pytest.fixture
def mock_responses():
    """Factory for creating mock responses"""
    return MockResponse
