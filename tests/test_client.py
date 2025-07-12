"""Unit tests for PlainClient class"""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from plain_mcp_server.server import PlainClient, PlainConfig


class TestPlainClient:
    """Test cases for PlainClient"""

    @pytest.mark.unit
    def test_client_initialization(self, mock_config):
        """Test client initialization with config"""
        client = PlainClient(mock_config)

        assert client.config == mock_config
        assert client.client is not None
        assert client.client.headers["Authorization"] == f"Bearer {mock_config.api_key}"
        assert client.client.headers["Content-Type"] == "application/json"

    @pytest.mark.unit
    async def test_execute_query_success(self, mock_config, mock_httpx_client):
        """Test successful GraphQL query execution"""
        client = PlainClient(mock_config)
        client.client = mock_httpx_client

        query = "query { test }"
        variables = {"var1": "value1"}

        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"data": {"test": "result"}}
        mock_httpx_client.post.return_value = mock_response

        result = await client.execute_query(query, variables)

        assert result == {"test": "result"}
        mock_httpx_client.post.assert_called_once_with(
            mock_config.base_url, json={"query": query, "variables": variables}
        )

    @pytest.mark.unit
    async def test_execute_query_with_graphql_errors(self, mock_config, mock_httpx_client):
        """Test GraphQL query with GraphQL errors"""
        client = PlainClient(mock_config)
        client.client = mock_httpx_client

        query = "query { test }"

        # Mock response with GraphQL errors
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "errors": [
                {"message": "Field 'test' not found"},
                {"message": "Invalid query"},
            ]
        }
        mock_httpx_client.post.return_value = mock_response

        with pytest.raises(Exception) as exc_info:
            await client.execute_query(query)

        assert "GraphQL errors" in str(exc_info.value)
        assert "Field 'test' not found" in str(exc_info.value)

    @pytest.mark.unit
    async def test_execute_query_http_error(self, mock_config, mock_httpx_client):
        """Test GraphQL query with HTTP error"""
        client = PlainClient(mock_config)
        client.client = mock_httpx_client

        query = "query { test }"

        # Mock HTTP error
        mock_httpx_client.post.side_effect = httpx.HTTPError("Network error")

        with pytest.raises(Exception) as exc_info:
            await client.execute_query(query)

        assert "HTTP error" in str(exc_info.value)

    @pytest.mark.unit
    async def test_execute_query_no_variables(self, mock_config, mock_httpx_client):
        """Test GraphQL query without variables"""
        client = PlainClient(mock_config)
        client.client = mock_httpx_client

        query = "query { test }"

        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"data": {"test": "result"}}
        mock_httpx_client.post.return_value = mock_response

        result = await client.execute_query(query)

        assert result == {"test": "result"}
        mock_httpx_client.post.assert_called_once_with(
            mock_config.base_url, json={"query": query, "variables": {}}
        )

    @pytest.mark.unit
    async def test_execute_query_response_without_data(self, mock_config, mock_httpx_client):
        """Test GraphQL query response without data field"""
        client = PlainClient(mock_config)
        client.client = mock_httpx_client

        query = "query { test }"

        # Mock response without data field
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {}
        mock_httpx_client.post.return_value = mock_response

        result = await client.execute_query(query)

        assert result == {}

    @pytest.mark.unit
    async def test_client_close(self, mock_config, mock_httpx_client):
        """Test client close method"""
        client = PlainClient(mock_config)
        client.client = mock_httpx_client

        await client.close()

        mock_httpx_client.aclose.assert_called_once()

    @pytest.mark.unit
    async def test_execute_query_json_decode_error(self, mock_config, mock_httpx_client):
        """Test GraphQL query with JSON decode error"""
        client = PlainClient(mock_config)
        client.client = mock_httpx_client

        query = "query { test }"

        # Mock response with JSON decode error
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_httpx_client.post.return_value = mock_response

        with pytest.raises(Exception):
            await client.execute_query(query)

    @pytest.mark.unit
    async def test_execute_query_timeout(self, mock_config):
        """Test GraphQL query timeout"""
        client = PlainClient(mock_config)

        # Mock timeout
        with patch.object(client.client, "post") as mock_post:
            mock_post.side_effect = httpx.TimeoutException("Request timed out")

            with pytest.raises(Exception) as exc_info:
                await client.execute_query("query { test }")

            assert "HTTP error" in str(exc_info.value)

    @pytest.mark.unit
    def test_config_validation(self):
        """Test PlainConfig validation"""
        # Test valid config
        config = PlainConfig(api_key="test_key")
        assert config.api_key == "test_key"
        assert config.base_url == "https://core-api.uk.plain.com/graphql/v1"

        # Test custom base_url
        config = PlainConfig(api_key="test_key", base_url="https://custom.example.com")
        assert config.base_url == "https://custom.example.com"

        # Test with workspace_id
        config = PlainConfig(api_key="test_key", workspace_id="workspace_123")
        assert config.workspace_id == "workspace_123"
