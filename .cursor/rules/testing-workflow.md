---
rule_type: always
title: Testing Workflow
description: Always run tests after code changes
---

# Testing Workflow

## Always Required After Code Changes

When you make any code changes to this Plain MCP Server project:

1. **Run `make test`** to execute all tests (62 tests, ~87% coverage)
2. **Check test coverage** - must maintain 80%+ coverage
3. **If tests fail**, fix the code before proceeding

## Available Test Commands

- `make test` - Run all tests
- `make test-unit` - Run unit tests only
- `make test-integration` - Run integration tests only
- `make test-coverage` - Run tests with HTML coverage report

## Test Structure

- Unit tests in `tests/` with `@pytest.mark.unit`
- Integration tests with `@pytest.mark.integration`

## Coverage Requirements

- **Minimum 80% test coverage** (configured in pytest settings)
- Add tests for new code to maintain coverage
