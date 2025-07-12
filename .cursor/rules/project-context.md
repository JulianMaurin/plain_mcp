---
rule_type: auto_attached
title: Project Context
description: Plain MCP Server project structure and conventions
---

# Plain MCP Server Context

## Project Overview

This is a Plain.com MCP (Model Context Protocol) Server that provides tools for interacting with Plain.com's customer support API. Uses Python 3.10+ with FastMCP.

## Key Files

- `plain_mcp_server/fastserver.py` - **Main implementation** (FastMCP server)
- `plain_mcp_server/server.py` - Legacy MCP server
- `tests/` - Test directory with unit and integration tests
- `pyproject.toml` - Project configuration and dependencies
- `Makefile` - Development commands

## Architecture

- **FastMCP server**: Primary implementation in `fastserver.py`
- **MCP tools**: All tools are async and return JSON strings
- **GraphQL client**: Interacts with Plain.com API via GraphQL
- **Environment variables**: `PLAIN_API_KEY` (required), `PLAIN_WORKSPACE_ID` (optional)

## Development Tips

- Use async/await patterns for MCP tools
- Proper GraphQL error handling with informative messages
- All MCP tools return JSON strings
- Use structured logging with appropriate log levels
- Run tests and linters after any code changes
