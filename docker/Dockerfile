FROM python:3.10.13-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml requirements.txt ./
COPY src/ ./src/
COPY pipelines/ ./pipelines/
COPY data/ ./data/

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -e .

# Expose ports for API and dashboard
EXPOSE 8000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["python", "-m", "pipelines.training_pipeline"]
RUN apt-get update && apt-get install -y make