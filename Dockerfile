# syntax=docker/dockerfile:1
FROM python:3.11-slim AS runtime

# Set environment flags
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=7860 \
    HOST=0.0.0.0 \
    HF_HOME=/app/.cache/huggingface \
    HF_HUB_DISABLE_SYMLINKS_WARNING=1

WORKDIR /app

# Install system utilities and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r ./backend/requirements.txt

# Copy source code, pre-built indices, and frontend assets
COPY backend ./backend
COPY frontend/dist ./frontend/dist
COPY .env.example ./.env.example

# Pre-download and cache embedding model weights inside the container image
# This ensures zero cold-start delay during live cloud deployment
RUN mkdir -p /app/.cache/huggingface && \
    python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-en-v1.5')"

# Create non-root user for security best practices
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 7860

# Healthcheck for cloud container orchestrators
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-7860}/api/health || exit 1

CMD ["sh", "-c", "exec uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-7860}"]
