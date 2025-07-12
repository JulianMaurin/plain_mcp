"""Integration tests for Plain.com MCP Server"""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from plain_mcp_server.server import PlainMCPServer


class TestPlainMCPIntegration:
    """Integration test cases for Plain.com MCP Server"""

    @pytest.mark.integration
    async def test_end_to_end_thread_workflow(self, mock_env_vars):
        """Test complete thread workflow from fetch to update"""
        server = PlainMCPServer()

        # Mock HTTP client
        mock_client = AsyncMock()

        # Mock responses for each step
        fetch_response = {
            "data": {
                "threads": {
                    "edges": [
                        {
                            "node": {
                                "id": "th_integration_test",
                                "title": "Integration Test Thread",
                                "status": "TODO",
                                "customer": {
                                    "id": "cust_integration",
                                    "fullName": "Integration Customer",
                                },
                            }
                        }
                    ],
                    "pageInfo": {"hasNextPage": False},
                }
            }
        }

        details_response = {
            "data": {
                "thread": {
                    "id": "th_integration_test",
                    "title": "Integration Test Thread",
                    "status": "TODO",
                    "timeline": {
                        "edges": [
                            {
                                "node": {
                                    "id": "timeline_1",
                                    "timestamp": "2024-01-01T10:00:00Z",
                                    "chat": {"text": "Need help with integration"},
                                }
                            }
                        ]
                    },
                }
            }
        }

        update_response = {
            "data": {
                "updateThread": {
                    "thread": {"id": "th_integration_test", "status": "DONE"},
                    "error": None,
                }
            }
        }

        note_response = {
            "data": {
                "createThreadNote": {
                    "threadNote": {
                        "id": "note_integration",
                        "text": "Resolved integration issue",
                    },
                    "error": None,
                }
            }
        }

        # Configure mock responses in sequence
        mock_client.post.side_effect = [
            MagicMock(status_code=200, json=lambda: fetch_response),
            MagicMock(status_code=200, json=lambda: details_response),
            MagicMock(status_code=200, json=lambda: update_response),
            MagicMock(status_code=200, json=lambda: note_response),
        ]

        # Initialize server and replace client
        await server.initialize()
        server.client.client = mock_client

        # Step 1: Fetch threads
        threads_result = await server._fetch_threads(status="TODO", limit=10)
        assert len(threads_result["threads"]) == 1
        assert threads_result["threads"][0]["id"] == "th_integration_test"

        # Step 2: Get thread details
        thread_details = await server._get_thread_details("th_integration_test")
        assert thread_details["id"] == "th_integration_test"
        assert "timeline" in thread_details

        # Step 3: Update thread status
        update_result = await server._update_thread_status("th_integration_test", "DONE")
        assert update_result["thread"]["status"] == "DONE"

        # Step 4: Add completion note
        note_result = await server._add_thread_note(
            "th_integration_test", "Resolved integration issue"
        )
        assert note_result["threadNote"]["text"] == "Resolved integration issue"

        # Verify all API calls were made
        assert mock_client.post.call_count == 4

    @pytest.mark.integration
    async def test_search_and_analyze_workflow(self, mock_env_vars):
        """Test search and pattern analysis workflow"""
        server = PlainMCPServer()

        # Mock HTTP client
        mock_client = AsyncMock()

        # Mock search response
        search_response = {
            "data": {
                "searchThreads": {
                    "edges": [
                        {
                            "node": {
                                "thread": {
                                    "id": "th_search_result",
                                    "title": "Login Issue",
                                    "status": "DONE",
                                }
                            }
                        }
                    ]
                }
            }
        }

        # Mock thread details for pattern analysis
        thread_details_response = {
            "data": {
                "thread": {
                    "id": "th_reference",
                    "title": "Login Problem",
                    "description": "User cannot login to account",
                }
            }
        }

        # Configure mock responses
        mock_client.post.side_effect = [
            MagicMock(status_code=200, json=lambda: search_response),
            MagicMock(status_code=200, json=lambda: thread_details_response),
            MagicMock(status_code=200, json=lambda: search_response),
        ]

        # Initialize server and replace client
        await server.initialize()
        server.client.client = mock_client

        # Step 1: Search for threads
        search_result = await server._search_threads("login issue", limit=10)
        assert len(search_result["results"]) == 1
        assert search_result["results"][0]["title"] == "Login Issue"

        # Step 2: Analyze patterns
        pattern_result = await server._analyze_thread_patterns("th_reference", days_back=30)
        assert "reference_thread" in pattern_result
        assert "similar_threads" in pattern_result
        assert pattern_result["reference_thread"]["id"] == "th_reference"

    @pytest.mark.integration
    async def test_customer_context_workflow(self, mock_env_vars):
        """Test customer context gathering workflow"""
        server = PlainMCPServer()

        # Mock HTTP client
        mock_client = AsyncMock()

        # Mock customer info response
        customer_response = {
            "data": {
                "customer": {
                    "id": "cust_workflow_test",
                    "fullName": "Workflow Test Customer",
                    "email": {"email": "workflow@test.com"},
                    "company": {"id": "comp_workflow", "name": "Workflow Test Company"},
                }
            }
        }

        # Mock customer threads response
        threads_response = {
            "data": {
                "threads": {
                    "edges": [
                        {
                            "node": {
                                "id": "th_customer_thread",
                                "title": "Customer Support Issue",
                                "status": "TODO",
                            }
                        }
                    ],
                    "pageInfo": {"hasNextPage": False},
                }
            }
        }

        # Configure mock responses
        mock_client.post.side_effect = [
            MagicMock(status_code=200, json=lambda: customer_response),
            MagicMock(status_code=200, json=lambda: threads_response),
        ]

        # Initialize server and replace client
        await server.initialize()
        server.client.client = mock_client

        # Step 1: Get customer info
        customer_info = await server._get_customer_info("cust_workflow_test")
        assert customer_info["fullName"] == "Workflow Test Customer"
        assert customer_info["company"]["name"] == "Workflow Test Company"

        # Step 2: Get customer's threads
        customer_threads = await server._fetch_threads(customer_id="cust_workflow_test")
        assert len(customer_threads["threads"]) == 1
        assert customer_threads["threads"][0]["title"] == "Customer Support Issue"

    @pytest.mark.integration
    async def test_error_handling_workflow(self, mock_env_vars):
        """Test error handling in various scenarios"""
        server = PlainMCPServer()

        # Mock HTTP client
        mock_client = AsyncMock()

        # Test GraphQL error
        error_response = {"errors": [{"message": "Thread not found"}, {"message": "Access denied"}]}

        mock_client.post.return_value = MagicMock(status_code=200, json=lambda: error_response)

        # Initialize server and replace client
        await server.initialize()
        server.client.client = mock_client

        # Test GraphQL error handling
        with pytest.raises(Exception) as exc_info:
            await server._get_thread_details("nonexistent_thread")

        assert "GraphQL errors" in str(exc_info.value)
        assert "Thread not found" in str(exc_info.value)

    @pytest.mark.integration
    async def test_http_error_handling(self, mock_env_vars):
        """Test HTTP error handling"""
        server = PlainMCPServer()

        # Mock HTTP client to raise HTTP error
        mock_client = AsyncMock()
        mock_client.post.side_effect = httpx.HTTPError("Connection failed")

        # Initialize server and replace client
        await server.initialize()
        server.client.client = mock_client

        # Test HTTP error handling
        with pytest.raises(Exception) as exc_info:
            await server._fetch_threads()

        assert "HTTP error" in str(exc_info.value)

    @pytest.mark.integration
    @pytest.mark.slow
    async def test_performance_with_large_dataset(self, mock_env_vars):
        """Test performance with large dataset (mock)"""
        server = PlainMCPServer()

        # Mock HTTP client
        mock_client = AsyncMock()

        # Create mock response with many threads
        large_threads = []
        for i in range(100):
            large_threads.append({
                "node": {
                    "id": f"th_perf_{i}",
                    "title": f"Performance Test Thread {i}",
                    "status": "TODO",
                }
            })

        large_response = {
            "data": {"threads": {"edges": large_threads, "pageInfo": {"hasNextPage": False}}}
        }

        mock_client.post.return_value = MagicMock(status_code=200, json=lambda: large_response)

        # Initialize server and replace client
        await server.initialize()
        server.client.client = mock_client

        # Test fetching large dataset
        result = await server._fetch_threads(limit=100)

        assert len(result["threads"]) == 100
        assert result["threads"][0]["id"] == "th_perf_0"
        assert result["threads"][99]["id"] == "th_perf_99"

    @pytest.mark.integration
    async def test_concurrent_operations(self, mock_env_vars):
        """Test concurrent operations"""
        import asyncio

        server = PlainMCPServer()

        # Mock HTTP client
        mock_client = AsyncMock()

        # Mock different responses for different operations
        def mock_response_factory(*args, **kwargs):
            # Extract the query from the request
            json_data = kwargs.get("json", {})
            query = json_data.get("query", "")

            if "threads(" in query:
                return MagicMock(
                    status_code=200,
                    json=lambda: {
                        "data": {"threads": {"edges": [], "pageInfo": {"hasNextPage": False}}}
                    },
                )
            elif "customer(" in query:
                return MagicMock(
                    status_code=200,
                    json=lambda: {
                        "data": {
                            "customer": {
                                "id": "cust_concurrent",
                                "fullName": "Concurrent Customer",
                            }
                        }
                    },
                )
            elif "searchThreads(" in query:
                return MagicMock(
                    status_code=200,
                    json=lambda: {"data": {"searchThreads": {"edges": []}}},
                )
            else:
                return MagicMock(status_code=200, json=lambda: {"data": {}})

        mock_client.post.side_effect = mock_response_factory

        # Initialize server and replace client
        await server.initialize()
        server.client.client = mock_client

        # Run concurrent operations
        tasks = [
            server._fetch_threads(status="TODO"),
            server._get_customer_info("cust_concurrent"),
            server._search_threads("concurrent test"),
            server._fetch_threads(status="DONE"),
        ]

        results = await asyncio.gather(*tasks)

        # Verify all operations completed
        assert len(results) == 4
        assert "threads" in results[0]  # fetch_threads
        assert "fullName" in results[1]  # get_customer_info
        assert "results" in results[2]  # search_threads
        assert "threads" in results[3]  # fetch_threads again
