---
rule_type: always
title: Linting Workflow
description: Always run linters after code changes
---

# Linting Workflow

## Always Required After Code Changes

When you make any code changes to this Plain MCP Server project:

1. **Run `make pre-commit`** to execute all code quality checks
2. **Fix any linting errors** before committing
3. **Pre-commit hooks will run automatically** on git commit

## What `make pre-commit` Does

Runs **Ruff** which handles everything:
- Code formatting (replaces Black)
- Linting (replaces flake8)
- Import sorting (replaces isort)
- Security checks (replaces Bandit)

## Code Quality Standards

- **Line length**: 100 characters maximum
- **Type hints required**: Use mypy-compatible type annotations
- **Python version**: Target Python 3.10+ (supports 3.10 to 3.13)
- **Structured logging**: Use appropriate log levels

## Configuration

All quality checks are configured in `pyproject.toml`:
- Ruff settings for formatting and linting
- MyPy type checking configuration
- Pytest settings for test execution
