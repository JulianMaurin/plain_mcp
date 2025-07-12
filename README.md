# Plain.com MCP Server

[![CI](https://github.com/JulianMaurin/plain_mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/JulianMaurin/plain_mcp/actions/workflows/ci.yml)

A Model Context Protocol (MCP) server for [Plain.com](https://plain.com) customer support operations. This server provides AI-friendly tools for managing support tickets, searching historical data, and automating customer support workflows.

## Features

🎫 **Support Ticket Management**
- Fetch support threads (tickets) with advanced filtering
- Update ticket status (TODO, DONE, SNOOZED)
- Add notes to tickets
- Get detailed ticket information including timeline

🔍 **Smart Search & Analysis**
- Search through support threads using text queries
- Analyze thread patterns to find similar issues
- Get insights from historical support data

👥 **Customer Management**
- Retrieve detailed customer information
- Access customer company and tenant details
- View customer support history

🤖 **AI-Powered Features**
- Designed specifically for AI assistant workflows
- Pattern recognition for similar support issues
- Contextual data retrieval for better support decisions

## Installation

### Prerequisites

- Python 3.10 or higher
- Plain.com account with API access

### For End Users

#### Install from Source

```bash
# Install directly from GitHub
pip install git+https://github.com/JulianMaurin/plain_mcp.git

# Or clone and install locally
git clone https://github.com/JulianMaurin/plain_mcp.git
cd plain_mcp
pip install .
```

#### Using Docker

```bash
# Build the Docker image
docker build -t plain-mcp-server https://github.com/JulianMaurin/plain_mcp.git

# Or use pre-built image (when available)
docker pull ghcr.io/julianmaurin/plain_mcp:latest
```

### For Developers

1. **Clone the repository:**
```bash
git clone https://github.com/JulianMaurin/plain_mcp.git
cd plain_mcp
```

2. **Setup development environment:**
```bash
# Install with development dependencies and pre-commit hooks
make setup
```

### Environment Configuration

Create environment variables for the API:

```bash
# Option 1: Set environment variables
export PLAIN_API_KEY=your_plain_api_key_here
export PLAIN_WORKSPACE_ID=your_workspace_id_here  # Optional

# Option 2: Create .env file (for development)
echo "PLAIN_API_KEY=your_plain_api_key_here" > .env
echo "PLAIN_WORKSPACE_ID=your_workspace_id_here" >> .env
```

### Verify Installation

```bash
# Test the server starts correctly
plain-mcp-server

# Or if installed in development mode
make run-server
```

## Usage

### Running the MCP Server

The server can be run using:
```bash
# Using make (recommended)
make run-server

# Or directly
python3 -m plain_mcp_server.fastserver

# Or using the installed script
plain-mcp-server
```

**Note**: The server uses the modern FastMCP implementation for better performance and simpler configuration.

### MCP Client Configuration

This server works with any IDE or application that supports the Model Context Protocol (MCP).

#### Using the Installed Script (Recommended)

After installing the package (see [Installation](#installation) section), use the `plain-mcp-server` command:

```json
{
  "mcpServers": {
    "plain-support": {
      "command": "plain-mcp-server",
      "env": {
        "PLAIN_API_KEY": "your_api_key_here",
        "PLAIN_WORKSPACE_ID": "your_workspace_id_here"
      }
    }
  }
}
```

#### Using Python Module

If you prefer to run as a module:

```json
{
  "mcpServers": {
    "plain-support": {
      "command": "python",
      "args": ["-m", "plain_mcp_server.fastserver"],
      "env": {
        "PLAIN_API_KEY": "your_api_key_here",
        "PLAIN_WORKSPACE_ID": "your_workspace_id_here"
      }
    }
  }
}
```

#### Docker Configuration

For Docker deployment:

```json
{
  "mcpServers": {
    "plain-support": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "--env-file", "/path/to/.env",
        "plain-mcp-server"
      ]
    }
  }
}
```

#### IDE-Specific Examples

**Claude Desktop:** Add to `claude_desktop_config.json`
**Cursor:** Configure in MCP settings
**VS Code:** Use MCP extension configuration
**Other IDEs:** Follow their MCP integration documentation

## Available Tools

### 1. `fetch_threads`
Fetch support threads with optional filters.

**Parameters:**
- `status` (optional): Filter by thread status (`TODO`, `DONE`, `SNOOZED`)
- `assignee_id` (optional): Filter by assigned user ID
- `customer_id` (optional): Filter by customer ID
- `limit` (optional): Maximum number of threads to return (default: 10)
- `include_resolved` (optional): Include resolved/done threads (default: false)

**Example:**
```json
{
  "status": "TODO",
  "limit": 5,
  "include_resolved": false
}
```

### 2. `search_threads`
Search through support threads using text search.

**Parameters:**
- `query` (required): Search query for thread content
- `limit` (optional): Maximum number of results (default: 10)

**Example:**
```json
{
  "query": "login issue password reset",
  "limit": 10
}
```

### 3. `get_thread_details`
Get detailed information about a specific thread including timeline.

**Parameters:**
- `thread_id` (required): Thread ID to get details for

**Example:**
```json
{
  "thread_id": "th_123456789"
}
```

### 4. `update_thread_status`
Update the status of a support thread.

**Parameters:**
- `thread_id` (required): Thread ID to update
- `status` (required): New status (`TODO`, `DONE`, `SNOOZED`)

**Example:**
```json
{
  "thread_id": "th_123456789",
  "status": "DONE"
}
```

### 5. `add_thread_note`
Add a note to a support thread.

**Parameters:**
- `thread_id` (required): Thread ID to add note to
- `content` (required): Note content

**Example:**
```json
{
  "thread_id": "th_123456789",
  "content": "Customer issue resolved via phone call. Follow-up scheduled for next week."
}
```

### 6. `get_customer_info`
Get detailed information about a customer.

**Parameters:**
- `customer_id` (required): Customer ID to get info for

**Example:**
```json
{
  "customer_id": "cust_123456789"
}
```

### 7. `analyze_thread_patterns`
Analyze patterns in threads to find similar issues.

**Parameters:**
- `thread_id` (required): Reference thread ID to find similar issues
- `days_back` (optional): Number of days to look back (default: 30)

**Example:**
```json
{
  "thread_id": "th_123456789",
  "days_back": 30
}
```

## AI Assistant Use Cases

### 1. **Daily Support Triage**
```
AI: "Show me all open support tickets from today"
→ Uses fetch_threads with status="TODO" and today's date filter
```

### 2. **Issue Pattern Analysis**
```
AI: "Find similar tickets to th_123456789 to understand common issues"
→ Uses analyze_thread_patterns to find related problems
```

### 3. **Customer Context Retrieval**
```
AI: "Get full context about customer cust_123456789 before responding"
→ Uses get_customer_info and fetch_threads with customer_id filter
```

### 4. **Automated Status Updates**
```
AI: "Mark ticket th_123456789 as resolved and add completion note"
→ Uses update_thread_status and add_thread_note
```

### 5. **Historical Search**
```
AI: "Search for previous tickets about 'API rate limiting' issues"
→ Uses search_threads with relevant keywords
```

## Error Handling

The server includes comprehensive error handling:

- **Authentication errors**: Invalid API keys
- **GraphQL errors**: API-specific errors from Plain.com
- **Network errors**: Connection issues
- **Validation errors**: Invalid parameters or missing data

All errors are returned in a structured format with descriptive messages.

## Development

### Running Tests

The project includes a comprehensive test suite with unit tests, integration tests, and mock API tests.

#### Quick Start
```bash
# Setup development environment (installs dependencies + pre-commit hooks)
make setup

# Run all tests
make test

# Run specific test types
make test-unit          # Unit tests only
make test-integration   # Integration tests only
make test-coverage      # Tests with coverage report
```

#### Additional Commands
```bash
# Show all available commands
make help

# Run pre-commit checks manually
make pre-commit
```

#### Using pytest directly
```bash
# Run all tests
pytest tests/ -v

# Run unit tests only
pytest tests/ -v -m unit

# Run integration tests only
pytest tests/ -v -m integration

# Run with coverage
pytest tests/ --cov=plain_mcp_server --cov-report=html

# Run specific test file
pytest tests/test_client.py -v

# Run specific test
pytest tests/test_client.py::TestPlainClient::test_client_initialization -v
```



### Test Structure

```
tests/
├── conftest.py           # Test configuration and fixtures
├── test_client.py        # Unit tests for PlainClient
├── test_server.py        # Unit tests for PlainMCPServer
├── test_integration.py   # Integration tests
└── test_data.py         # Test data and utilities
```

### Test Coverage

The test suite includes:
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test complete workflows and component interactions
- **Mock API Tests**: Test with mocked Plain.com API responses
- **Error Handling Tests**: Test error scenarios and edge cases
- **Performance Tests**: Test with large datasets and concurrent operations

### Code Quality

This project uses pre-commit hooks to ensure code quality automatically. Run `make setup` to install all dependencies and hooks.

**Ruff** handles all code formatting, linting, import sorting, and security checks in a single fast tool, replacing Black, isort, flake8, and most Bandit checks.

#### Manual Code Quality Checks
```bash
# Run all pre-commit hooks manually
make pre-commit

# Run individual tools (if needed)
ruff check .                    # Linting and security checks
ruff format .                   # Code formatting
mypy plain_mcp_server/         # Type checking
```

#### Pre-commit Hooks Include:
- **Ruff**: Code formatting, linting, import sorting, and security checks
- **MyPy**: Type checking (main package only)
- **Standard hooks**: Trailing whitespace, file endings, YAML/JSON validation

Hooks run automatically on every `git commit`, ensuring consistent code quality.

### Quick Reference

**Essential Commands:**
- `make setup` - Complete development environment setup
- `make test` - Run all tests
- `make test-coverage` - Run tests with coverage report
- `make pre-commit` - Run code quality checks manually
- `make run-server` - Start the MCP server
- `make help` - Show all available commands

## Contributing

1. Fork the repository
2. Create a feature branch
3. Setup development environment: `make setup`
4. Make your changes
5. Add tests for new functionality
6. Run the test suite: `make test`
7. Pre-commit hooks will run automatically on commit
8. Submit a pull request

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Support

For issues and questions:
- Create an issue in the GitHub repository
- Check the Plain.com API documentation
- Review the MCP protocol specification

## Changelog

### v0.1.0
- Initial release
- Basic thread management operations
- Search and analysis capabilities
- Customer information retrieval
- AI-optimized tool interfaces
