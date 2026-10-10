# =============================================================================
# Production Dockerfile for NDA Multi-Label Clause Classification Backend
# =============================================================================
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HF_HUB_DISABLE_SYMLINKS_WARNING=1 \
    PORT=8000

# Set working directory
WORKDIR /app

# Install minimal system build requirements
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency requirements first for layer caching
COPY requirements.txt ./

# Install Python packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend application source code and configurations
COPY backend /app/backend
COPY configs /app/configs

# Create runtime storage directory
RUN mkdir -p /app/storage

# Create non-root system user for container security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose FastAPI listening port
EXPOSE 8000

# Health check instruction
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Launch production Uvicorn server
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
