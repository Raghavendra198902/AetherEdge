# 🎨 Brahma Blueprint Engine Dockerfile
# ====================================

FROM python:3.11-slim-bullseye

# Set divine metadata
LABEL maintainer="AetherEdge Team <brahma@aetheredge.com>"
LABEL version="1.0.0"
LABEL description="Brahma Divine Blueprint Engine - Infrastructure blueprint generation service"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH="/opt/venv/bin:$PATH"

# Create non-root user for security
RUN groupadd -r brahma && useradd -r -g brahma brahma

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        libpq-dev \
        && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/templates /app/models /app/tmp && \
    chown -R brahma:brahma /app

# Switch to non-root user
USER brahma

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Default command
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8001"]
