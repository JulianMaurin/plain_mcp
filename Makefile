.PHONY: help install setup test test-unit test-integration test-coverage clean pre-commit run-server docker-build docker-run

# Default target
help: ## Show this help message
	@echo "📋 Plain.com MCP Server - Development Commands"
	@echo "=" | tr -d '\n' | while read -r line; do printf "=%.0s" {1..50}; done; echo
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "💡 Code quality checks are handled by pre-commit hooks."

# Setup
install: ## Install dependencies
	pip install -r requirements.txt

setup: install ## Setup development environment
	pre-commit install
	@echo "✅ Development environment ready!"

# Testing
test: ## Run all tests
	python -m pytest tests/ -v

test-unit: ## Run unit tests only
	python -m pytest tests/ -v -m unit

test-integration: ## Run integration tests only
	python -m pytest tests/ -v -m integration

test-coverage: ## Run tests with coverage report
	python -m pytest tests/ --cov=plain_mcp_server --cov-report=html --cov-report=term-missing
	@echo "📊 Coverage report: htmlcov/index.html"

# Code quality
pre-commit: ## Run pre-commit on all files
	pre-commit run --all-files

# Server
run-server: ## Start the MCP server
	python -m plain_mcp_server.fastserver

# Docker
docker-build: ## Build Docker image
	docker build -t plain-mcp-server .

docker-run: ## Run Docker container
	docker run -it --rm --env-file .env plain-mcp-server

# Cleanup
clean: ## Clean up generated files
	rm -rf .pytest_cache/ htmlcov/ .coverage .mypy_cache/ .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
