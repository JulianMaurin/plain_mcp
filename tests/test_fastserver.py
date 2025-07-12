"""Tests for FastMCP server implementation"""

import json
import os
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from plain_mcp_server.fastserver import (
    PlainClient,
    PlainConfig,
    add_thread_note,
    analyze_thread_patterns,
    fetch_threads,
    get_client,
    get_customer_info,
    get_thread_details,
    mcp_server,
    search_threads,
    update_thread_status,
)


class TestFastMCPServer:
    """Test cases for FastMCP server implementation"""

    @pytest.mark.unit
    def test_mcp_server_initialization(self):
        """Test that MCP server initializes correctly"""
        assert mcp_server is not None
        assert mcp_server.name == "plain-mcp-server"

    @pytest.mark.unit
    def test_plain_config(self):
        """Test PlainConfig model"""
        config = PlainConfig(api_key="test_key")
        assert config.api_key == "test_key"
        assert config.base_url == "https://core-api.uk.plain.com/graphql/v1"
        assert config.workspace_id is None

    @pytest.mark.unit
    def test_plain_client_initialization(self):
        """Test PlainClient initialization"""
        config = PlainConfig(api_key="test_key")
        client = PlainClient(config)

        assert client.config == config
        assert client.client is not None

    @pytest.mark.unit
    async def test_get_client_with_env_var(self, mock_env_vars):
        """Test getting client with environment variable"""
        # Clear any existing client
        import plain_mcp_server.fastserver as fastserver

        fastserver.plain_client = None

        client = await get_client()
        assert client is not None
        assert isinstance(client, PlainClient)

    @pytest.mark.unit
    async def test_get_client_without_env_var(self):
        """Test getting client without API key raises error"""
        # Clear any existing client
        import plain_mcp_server.fastserver as fastserver

        fastserver.plain_client = None

        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                await get_client()

            assert "PLAIN_API_KEY environment variable is required" in str(exc_info.value)

    @pytest.mark.unit
    @patch("plain_mcp_server.fastserver.get_client")
    async def test_fetch_threads_tool(self, mock_get_client):
        """Test fetch_threads tool function"""
        # Mock the client and response
        mock_client = AsyncMock()
        mock_client.execute_query.return_value = {
            "threads": {
                "edges": [
                    {
                        "node": {
                            "id": "th_test123",
                            "title": "Test Thread",
                            "status": "TODO",
                        }
                    }
                ],
                "pageInfo": {"hasNextPage": False},
            }
        }
        mock_get_client.return_value = mock_client

        # Test the tool
        result = await fetch_threads(status="TODO", limit=5)
        result_data = json.loads(result)

        assert "threads" in result_data
        assert "hasMore" in result_data
        assert len(result_data["threads"]) == 1
        assert result_data["threads"][0]["id"] == "th_test123"
        assert result_data["hasMore"] is False

    @pytest.mark.unit
    @patch("plain_mcp_server.fastserver.get_client")
    async def test_search_threads_tool(self, mock_get_client):
        """Test search_threads tool function"""
        # Mock the client and response
        mock_client = AsyncMock()
        mock_client.execute_query.return_value = {
            "searchThreads": {
                "edges": [
                    {
                        "node": {
                            "thread": {
                                "id": "th_search123",
                                "title": "Search Result",
                                "status": "TODO",
                            }
                        }
                    }
                ]
            }
        }
        mock_get_client.return_value = mock_client

        # Test the tool
        result = await search_threads("test query", limit=10)
        result_data = json.loads(result)

        assert "results" in result_data
        assert len(result_data["results"]) == 1
        assert result_data["results"][0]["id"] == "th_search123"

    @pytest.mark.unit
    @patch("plain_mcp_server.fastserver.get_client")
    async def test_get_thread_details_tool(self, mock_get_client):
        """Test get_thread_details tool function"""
        # Mock the client and response
        mock_client = AsyncMock()
        mock_client.execute_query.return_value = {
            "thread": {
                "id": "th_details123",
                "title": "Detailed Thread",
                "status": "TODO",
                "timeline": {
                    "edges": [
                        {
                            "node": {
                                "id": "timeline_1",
                                "timestamp": "2024-01-01T10:00:00Z",
                            }
                        }
                    ]
                },
            }
        }
        mock_get_client.return_value = mock_client

        # Test the tool
        result = await get_thread_details("th_details123")
        result_data = json.loads(result)

        assert result_data["id"] == "th_details123"
        assert result_data["title"] == "Detailed Thread"
        assert "timeline" in result_data

    @pytest.mark.unit
    @patch("plain_mcp_server.fastserver.get_client")
    async def test_update_thread_status_tool(self, mock_get_client):
        """Test update_thread_status tool function"""
        # Mock the client and response
        mock_client = AsyncMock()
        mock_client.execute_query.return_value = {
            "updateThread": {
                "thread": {
                    "id": "th_update123",
                    "status": "DONE",
                    "statusChangedAt": "2024-01-01T11:00:00Z",
                },
                "error": None,
            }
        }
        mock_get_client.return_value = mock_client

        # Test the tool
        result = await update_thread_status("th_update123", "DONE")
        result_data = json.loads(result)

        assert result_data["thread"]["status"] == "DONE"
        assert result_data["error"] is None

    @pytest.mark.unit
    @patch("plain_mcp_server.fastserver.get_client")
    async def test_add_thread_note_tool(self, mock_get_client):
        """Test add_thread_note tool function"""
        # Mock the client and response
        mock_client = AsyncMock()
        mock_client.execute_query.return_value = {
            "createThreadNote": {
                "threadNote": {
                    "id": "note_123",
                    "text": "Test note",
                    "createdAt": "2024-01-01T11:00:00Z",
                },
                "error": None,
            }
        }
        mock_get_client.return_value = mock_client

        # Test the tool
        result = await add_thread_note("th_note123", "Test note")
        result_data = json.loads(result)

        assert result_data["threadNote"]["text"] == "Test note"
        assert result_data["error"] is None

    @pytest.mark.unit
    @patch("plain_mcp_server.fastserver.get_client")
    async def test_get_customer_info_tool(self, mock_get_client):
        """Test get_customer_info tool function"""
        # Mock the client and response
        mock_client = AsyncMock()
        mock_client.execute_query.return_value = {
            "customer": {
                "id": "cust_test123",
                "fullName": "Test Customer",
                "email": {"email": "test@example.com", "isVerified": True},
            }
        }
        mock_get_client.return_value = mock_client

        # Test the tool
        result = await get_customer_info("cust_test123")
        result_data = json.loads(result)

        assert result_data["id"] == "cust_test123"
        assert result_data["fullName"] == "Test Customer"
        assert result_data["email"]["email"] == "test@example.com"

    @pytest.mark.unit
    @patch("plain_mcp_server.fastserver.get_thread_details")
    @patch("plain_mcp_server.fastserver.search_threads")
    async def test_analyze_thread_patterns_tool(self, mock_search, mock_details, mock_env_vars):
        """Test analyze_thread_patterns tool function"""
        # Clear any existing client
        import plain_mcp_server.fastserver as fastserver

        fastserver.plain_client = None

        # Mock the thread details response
        thread_details = {
            "id": "th_pattern123",
            "title": "Pattern Analysis",
            "description": "Test description",
            "status": "TODO",
        }
        mock_details.return_value = json.dumps(thread_details)

        # Mock the search response
        search_results = {
            "results": [
                {"id": "th_similar1", "title": "Similar Thread 1"},
                {"id": "th_similar2", "title": "Similar Thread 2"},
            ]
        }
        mock_search.return_value = json.dumps(search_results)

        # Test the tool
        result = await analyze_thread_patterns("th_pattern123", days_back=30)
        result_data = json.loads(result)

        assert "reference_thread" in result_data
        assert "similar_threads" in result_data
        assert "analysis" in result_data
        assert result_data["reference_thread"]["id"] == "th_pattern123"
        assert len(result_data["similar_threads"]) == 2

    @pytest.mark.unit
    @patch("plain_mcp_server.fastserver.get_thread_details")
    async def test_analyze_thread_patterns_thread_not_found(self, mock_details, mock_env_vars):
        """Test analyze_thread_patterns when thread not found"""
        # Clear any existing client
        import plain_mcp_server.fastserver as fastserver

        fastserver.plain_client = None

        # Mock empty thread details response
        mock_details.return_value = json.dumps({})

        # Test the tool
        result = await analyze_thread_patterns("th_nonexistent")
        result_data = json.loads(result)

        assert result_data == {"error": "Thread not found"}

    @pytest.mark.integration
    async def test_tool_error_handling(self, mock_env_vars):
        """Test error handling in FastMCP tools"""
        import plain_mcp_server.fastserver as fastserver

        # Clear any existing client
        fastserver.plain_client = None

        # Test tool call without API key - should raise exception
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                await fetch_threads()

            assert "PLAIN_API_KEY environment variable is required" in str(exc_info.value)

    @pytest.mark.integration
    async def test_mcp_server_tool_discovery(self):
        """Test that MCP server properly registers all tools"""
        # Test that all expected tools are registered
        expected_tools = [
            "fetch_threads",
            "search_threads",
            "get_thread_details",
            "update_thread_status",
            "add_thread_note",
            "get_customer_info",
            "analyze_thread_patterns",
        ]

        # Check that all tools are registered in the server
        server_tools = [tool.name for tool in await mcp_server.list_tools()]

        for expected_tool in expected_tools:
            assert expected_tool in server_tools, f"Tool {expected_tool} not found in server"

    @pytest.mark.integration
    @patch("plain_mcp_server.fastserver.get_client")
    async def test_mcp_tool_integration_flow(self, mock_get_client):
        """Test complete MCP tool integration flow"""
        # Mock the client and response
        mock_client = AsyncMock()
        mock_client.execute_query.return_value = {
            "threads": {
                "edges": [
                    {
                        "node": {
                            "id": "th_integration123",
                            "title": "Integration Test Thread",
                            "status": "TODO",
                        }
                    }
                ],
                "pageInfo": {"hasNextPage": False},
            }
        }
        mock_get_client.return_value = mock_client

        # Test tool call through MCP server
        result = await fetch_threads(status="TODO", limit=5)
        result_data = json.loads(result)

        # Verify MCP response format
        assert "threads" in result_data
        assert "hasMore" in result_data
        assert len(result_data["threads"]) == 1
        assert result_data["threads"][0]["id"] == "th_integration123"

    @pytest.mark.integration
    @patch("plain_mcp_server.fastserver.get_client")
    async def test_mcp_error_handling_flow(self, mock_get_client):
        """Test error handling through MCP protocol"""
        # Mock the client to raise an exception
        mock_client = AsyncMock()
        mock_client.execute_query.side_effect = Exception("Test API error")
        mock_get_client.return_value = mock_client

        # Test error handling - should raise exception (FastMCP framework handles it)
        with pytest.raises(Exception) as exc_info:
            await fetch_threads()

        assert "Test API error" in str(exc_info.value)

    @pytest.mark.integration
    @patch("plain_mcp_server.fastserver.get_client")
    async def test_mcp_tool_validation(self, mock_get_client):
        """Test MCP tool parameter validation"""
        # Mock the client
        mock_client = AsyncMock()
        mock_client.execute_query.return_value = {
            "threads": {"edges": [], "pageInfo": {"hasNextPage": False}}
        }
        mock_get_client.return_value = mock_client

        # Test with invalid parameters (should handle gracefully)
        result = await fetch_threads(status="INVALID_STATUS", limit=-1)
        result_data = json.loads(result)

        # Should still work (validation happens at API level)
        assert "threads" in result_data
        assert "hasMore" in result_data

    @pytest.mark.integration
    async def test_mcp_server_metadata(self):
        """Test MCP server metadata and configuration"""
        # Test server has proper metadata
        assert mcp_server.name == "plain-mcp-server"

        # Test that server has tools registered
        tools = await mcp_server.list_tools()
        assert len(tools) == 7  # Should have 7 tools

        # Test tool metadata
        tool_names = [tool.name for tool in tools]
        assert "fetch_threads" in tool_names
        assert "search_threads" in tool_names
        assert "get_thread_details" in tool_names
        assert "update_thread_status" in tool_names
        assert "add_thread_note" in tool_names
        assert "get_customer_info" in tool_names
        assert "analyze_thread_patterns" in tool_names

    @pytest.mark.integration
    @patch("plain_mcp_server.fastserver.get_client")
    async def test_concurrent_mcp_tool_calls(self, mock_get_client):
        """Test concurrent MCP tool calls"""
        import asyncio

        # Mock the client with different responses
        mock_client = AsyncMock()

        def mock_response_factory(*args, **kwargs):
            query = args[0] if args else ""
            if "threads(" in query:
                return {
                    "threads": {
                        "edges": [
                            {
                                "node": {
                                    "id": "th_concurrent",
                                    "title": "Concurrent Test",
                                }
                            }
                        ],
                        "pageInfo": {"hasNextPage": False},
                    }
                }
            elif "customer(" in query:
                return {
                    "customer": {
                        "id": "cust_concurrent",
                        "fullName": "Concurrent Customer",
                    }
                }
            elif "searchThreads(" in query:
                return {"searchThreads": {"edges": []}}
            else:
                return {"data": {}}

        mock_client.execute_query.side_effect = mock_response_factory
        mock_get_client.return_value = mock_client

        # Run concurrent tool calls
        tasks = [
            fetch_threads(status="TODO"),
            get_customer_info("cust_concurrent"),
            search_threads("concurrent test"),
        ]

        results = await asyncio.gather(*tasks)

        # Verify all calls completed
        assert len(results) == 3
        for result in results:
            result_data = json.loads(result)
            assert "error" not in result_data  # No errors

    @pytest.mark.integration
    @patch("plain_mcp_server.fastserver.get_client")
    async def test_mcp_tool_data_consistency(self, mock_get_client):
        """Test data consistency across MCP tool calls"""
        # Mock the client
        mock_client = AsyncMock()
        thread_data = {
            "id": "th_consistency123",
            "title": "Consistency Test Thread",
            "status": "TODO",
            "timeline": {
                "edges": [{"node": {"id": "timeline_1", "timestamp": "2024-01-01T10:00:00Z"}}]
            },
        }

        # Mock responses for different calls
        mock_client.execute_query.side_effect = [
            {
                "threads": {
                    "edges": [{"node": thread_data}],
                    "pageInfo": {"hasNextPage": False},
                }
            },
            {"thread": thread_data},
        ]
        mock_get_client.return_value = mock_client

        # Test data consistency between fetch_threads and get_thread_details
        threads_result = await fetch_threads(status="TODO")
        details_result = await get_thread_details("th_consistency123")

        threads_data = json.loads(threads_result)
        details_data = json.loads(details_result)

        # Verify data consistency
        assert threads_data["threads"][0]["id"] == details_data["id"]
        assert threads_data["threads"][0]["title"] == details_data["title"]
        assert threads_data["threads"][0]["status"] == details_data["status"]

    @pytest.mark.integration
    async def test_plain_client_error_handling(self):
        """Test PlainClient error handling paths"""
        config = PlainConfig(api_key="test_key")
        client = PlainClient(config)

        # Test HTTP error handling
        with patch.object(client.client, "post") as mock_post:
            mock_post.side_effect = httpx.HTTPError("Connection failed")

            with pytest.raises(Exception) as exc_info:
                await client.execute_query("test query")

            assert "HTTP error" in str(exc_info.value)

        # Test GraphQL error handling
        with patch.object(client.client, "post") as mock_post:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "errors": [
                    {"message": "Test GraphQL error"},
                    {"message": "Another error"},
                ]
            }
            mock_post.return_value = mock_response

            with pytest.raises(Exception) as exc_info:
                await client.execute_query("test query")

            assert "GraphQL errors" in str(exc_info.value)
            assert "Test GraphQL error" in str(exc_info.value)

        # Test JSON decode error handling
        with patch.object(client.client, "post") as mock_post:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
            mock_post.return_value = mock_response

            with pytest.raises(Exception):
                await client.execute_query("test query")

        # Test client close
        with patch.object(client.client, "aclose") as mock_aclose:
            await client.close()
            mock_aclose.assert_called_once()

    @pytest.mark.integration
    async def test_get_client_logger_coverage(self):
        """Test logger coverage in get_client"""
        import plain_mcp_server.fastserver as fastserver

        # Clear any existing client
        fastserver.plain_client = None

        with patch.dict(os.environ, {"PLAIN_API_KEY": "test_key"}):
            with patch("plain_mcp_server.fastserver.logger") as mock_logger:
                await get_client()
                mock_logger.info.assert_called_with("Plain.com client initialized successfully")

    @pytest.mark.integration
    async def test_analyze_thread_patterns_coverage(self):
        """Test analyze_thread_patterns with detailed coverage"""
        with patch("plain_mcp_server.fastserver.get_thread_details") as mock_details:
            with patch("plain_mcp_server.fastserver.search_threads") as mock_search:
                # Test with thread found
                mock_details.return_value = json.dumps({
                    "id": "th_test123",
                    "title": "Test Thread",
                    "description": "Test description",
                    "status": "TODO",
                })
                mock_search.return_value = json.dumps({
                    "results": [
                        {"id": "th_similar1", "title": "Similar 1"},
                        {
                            "id": "th_test123",
                            "title": "Test Thread",
                        },  # Should be filtered out
                        {"id": "th_similar2", "title": "Similar 2"},
                    ]
                })

                result = await analyze_thread_patterns("th_test123")
                result_data = json.loads(result)

                assert result_data["reference_thread"]["id"] == "th_test123"
                assert len(result_data["similar_threads"]) == 2  # Original thread filtered out
                assert result_data["analysis"]["total_found"] == 2

                # Test with thread not found
                mock_details.return_value = json.dumps({})

                result = await analyze_thread_patterns("th_nonexistent")
                result_data = json.loads(result)

                assert "error" in result_data
                assert result_data["error"] == "Thread not found"

    @pytest.mark.integration
    def test_main_function_coverage(self):
        """Test main function for coverage"""
        with patch("plain_mcp_server.fastserver.logger") as mock_logger:
            with patch("plain_mcp_server.fastserver.mcp_server") as mock_server:
                from plain_mcp_server.fastserver import main

                # Mock the server run method to avoid actually starting the server
                mock_server.run.return_value = None

                main()

                mock_logger.info.assert_called_with("Starting Plain.com MCP Server...")
                mock_server.run.assert_called_with()

    @pytest.mark.integration
    async def test_filters_coverage_in_fetch_threads(self):
        """Test comprehensive filter coverage in fetch_threads"""
        with patch("plain_mcp_server.fastserver.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.execute_query.return_value = {
                "threads": {"edges": [], "pageInfo": {"hasNextPage": False}}
            }
            mock_get_client.return_value = mock_client

            # Test with no filters (should add default filter)
            await fetch_threads()

            # Test with all filters
            await fetch_threads(
                status="TODO",
                assignee_id="user123",
                customer_id="cust123",
                limit=5,
                include_resolved=True,
            )

            # Test with include_resolved=False (default)
            await fetch_threads(include_resolved=False)

            # Verify client was called multiple times
            assert mock_client.execute_query.call_count >= 3

    @pytest.mark.integration
    async def test_http_response_error_handling(self):
        """Test HTTP response error handling"""
        config = PlainConfig(api_key="test_key")
        client = PlainClient(config)

        # Test HTTP status error
        with patch.object(client.client, "post") as mock_post:
            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "404 Not Found", request=MagicMock(), response=MagicMock()
            )
            mock_post.return_value = mock_response

            with pytest.raises(Exception) as exc_info:
                await client.execute_query("test query")

            assert "HTTP error" in str(exc_info.value)

    @pytest.mark.integration
    async def test_empty_response_handling(self):
        """Test handling of empty or malformed responses"""
        config = PlainConfig(api_key="test_key")
        client = PlainClient(config)

        # Test response without data field
        with patch.object(client.client, "post") as mock_post:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {}  # No data field
            mock_post.return_value = mock_response

            result = await client.execute_query("test query")
            assert result == {}  # Should return empty dict when no data

        # Test response with data field
        with patch.object(client.client, "post") as mock_post:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {"data": {"test": "value"}}
            mock_post.return_value = mock_response

            result = await client.execute_query("test query")
            assert result == {"test": "value"}
