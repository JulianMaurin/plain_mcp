# Use Python 3.13 as base image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create app directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy package metadata and source code
COPY pyproject.toml README.md ./
COPY plain_mcp_server/ plain_mcp_server/

# Install the package with production dependencies only
RUN pip install .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Default command
CMD ["python", "-m", "plain_mcp_server.fastserver"]
