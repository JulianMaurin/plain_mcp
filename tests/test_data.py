"""Test data and utilities for Plain.com MCP Server tests"""

from typing import Any, Optional

# Sample thread data for testing
SAMPLE_THREAD = {
    "id": "th_sample123",
    "title": "Sample Support Thread",
    "description": "This is a sample support thread for testing",
    "status": "TODO",
    "statusChangedAt": "2024-01-01T10:00:00Z",
    "assignedToUser": {"id": "user_123", "fullName": "Sample User"},
    "customer": {
        "id": "cust_456",
        "fullName": "Sample Customer",
        "email": {"email": "sample@example.com"},
    },
    "createdAt": "2024-01-01T09:00:00Z",
    "updatedAt": "2024-01-01T10:00:00Z",
    "priority": "HIGH",
    "labels": [{"id": "label_789", "labelType": {"name": "Bug"}}],
}

# Sample customer data for testing
SAMPLE_CUSTOMER = {
    "id": "cust_sample456",
    "fullName": "Sample Customer",
    "email": {"email": "customer@example.com", "isVerified": True},
    "company": {
        "id": "comp_789",
        "name": "Sample Company",
        "domainName": "example.com",
    },
    "createdAt": "2024-01-01T08:00:00Z",
    "updatedAt": "2024-01-01T09:00:00Z",
    "tenantMemberships": {
        "edges": [{"node": {"tenant": {"id": "tenant_111", "name": "Sample Tenant"}}}]
    },
}

# Sample timeline data for testing
SAMPLE_TIMELINE = {
    "edges": [
        {
            "node": {
                "id": "timeline_1",
                "timestamp": "2024-01-01T09:30:00Z",
                "actor": {"user": {"id": "user_123", "fullName": "Sample User"}},
                "chat": {"text": "Hello, I need help with my account"},
            }
        },
        {
            "node": {
                "id": "timeline_2",
                "timestamp": "2024-01-01T09:45:00Z",
                "actor": {"user": {"id": "user_123", "fullName": "Sample User"}},
                "note": {"text": "Customer contacted via email"},
            }
        },
    ]
}

# GraphQL response templates
GRAPHQL_RESPONSES = {
    "threads": {
        "data": {
            "threads": {
                "edges": [{"node": SAMPLE_THREAD}],
                "pageInfo": {"hasNextPage": False, "endCursor": None},
            }
        }
    },
    "thread_details": {"data": {"thread": {**SAMPLE_THREAD, "timeline": SAMPLE_TIMELINE}}},
    "search_threads": {"data": {"searchThreads": {"edges": [{"node": {"thread": SAMPLE_THREAD}}]}}},
    "customer": {"data": {"customer": SAMPLE_CUSTOMER}},
    "update_thread": {
        "data": {
            "updateThread": {
                "thread": {
                    "id": "th_sample123",
                    "status": "DONE",
                    "statusChangedAt": "2024-01-01T11:00:00Z",
                },
                "error": None,
            }
        }
    },
    "create_note": {
        "data": {
            "createThreadNote": {
                "threadNote": {
                    "id": "note_123",
                    "text": "Sample note",
                    "createdAt": "2024-01-01T11:00:00Z",
                },
                "error": None,
            }
        }
    },
    "graphql_error": {"errors": [{"message": "Thread not found"}, {"message": "Access denied"}]},
}


def create_mock_threads(count: int) -> list[dict[str, Any]]:
    """Create a list of mock thread data"""
    threads = []
    for i in range(count):
        thread = SAMPLE_THREAD.copy()
        thread["id"] = f"th_mock_{i}"
        thread["title"] = f"Mock Thread {i}"
        threads.append(thread)
    return threads


def create_threads_response(
    threads: list[dict[str, Any]], has_next_page: bool = False
) -> dict[str, Any]:
    """Create a GraphQL threads response"""
    return {
        "data": {
            "threads": {
                "edges": [{"node": thread} for thread in threads],
                "pageInfo": {
                    "hasNextPage": has_next_page,
                    "endCursor": threads[-1]["id"] if threads else None,
                },
            }
        }
    }


def create_search_response(threads: list[dict[str, Any]]) -> dict[str, Any]:
    """Create a GraphQL search response"""
    return {
        "data": {"searchThreads": {"edges": [{"node": {"thread": thread}} for thread in threads]}}
    }


def create_error_response(error_messages: list[str]) -> dict[str, Any]:
    """Create a GraphQL error response"""
    return {"errors": [{"message": msg} for msg in error_messages]}


class MockGraphQLClient:
    """Mock GraphQL client for testing"""

    def __init__(self, responses: Optional[dict[str, Any]] = None):
        self.responses = responses if responses is not None else GRAPHQL_RESPONSES
        self.call_count = 0
        self.last_query = None
        self.last_variables = None

    async def post(self, url: str, json: dict[str, Any]):
        """Mock POST request"""
        self.call_count += 1
        self.last_query = json.get("query", "")
        self.last_variables = json.get("variables", {})

        # Determine response based on query content
        if "threads" in self.last_query and "searchThreads" not in self.last_query:
            return self._create_mock_response(self.responses["threads"])
        elif "searchThreads" in self.last_query:
            return self._create_mock_response(self.responses["search_threads"])
        elif "thread(" in self.last_query:
            return self._create_mock_response(self.responses["thread_details"])
        elif "customer(" in self.last_query:
            return self._create_mock_response(self.responses["customer"])
        elif "updateThread" in self.last_query:
            return self._create_mock_response(self.responses["update_thread"])
        elif "createThreadNote" in self.last_query:
            return self._create_mock_response(self.responses["create_note"])
        else:
            return self._create_mock_response({"data": {}})

    def _create_mock_response(self, response_data: dict[str, Any]):
        """Create a mock HTTP response"""

        class MockResponse:
            def __init__(self, data):
                self.data = data
                self.status_code = 200

            def json(self):
                return self.data

            def raise_for_status(self):
                pass

        return MockResponse(response_data)


# Test utilities
def assert_thread_structure(thread: dict[str, Any]):
    """Assert that a thread has the expected structure"""
    required_fields = ["id", "title", "status", "createdAt", "updatedAt"]
    for field in required_fields:
        assert field in thread, f"Thread missing required field: {field}"

    if "customer" in thread:
        assert "id" in thread["customer"]
        assert "fullName" in thread["customer"]


def assert_customer_structure(customer: dict[str, Any]):
    """Assert that a customer has the expected structure"""
    required_fields = ["id", "fullName", "email", "createdAt", "updatedAt"]
    for field in required_fields:
        assert field in customer, f"Customer missing required field: {field}"

    assert "email" in customer["email"]


def assert_mcp_response_structure(response):
    """Assert that an MCP response has the expected structure"""
    assert hasattr(response, "content")
    assert len(response.content) > 0
    assert response.content[0].type == "text"
