---
rule_type: always
title: Conventional Commits
description: Use conventional commit format for all commits
---

# Conventional Commits

## Required Format

Use this format for **all commits**:

```
<type>(<scope>): <description>
```

## Types

- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks (dependencies, build, etc.)
- `ci`: CI/CD changes

## Scopes (Optional)

- `server`: Core server functionality
- `client`: Plain.com API client
- `tools`: MCP tools implementation
- `docker`: Docker-related changes
- `tests`: Test-related changes
- `deps`: Dependencies

## Examples

- `feat(server): add new thread search functionality`
- `fix(client): handle GraphQL errors properly`
- `test(tools): add integration tests for fetch_threads`
- `chore(deps): update mcp to version 1.1.0`
- `ci: add Python 3.13 to test matrix`
- `docs: update README with Docker instructions`

## Description Guidelines

- Use present tense ("add" not "added")
- Use imperative mood ("move cursor to..." not "moves cursor to...")
- Don't capitalize first letter
- No period at the end
