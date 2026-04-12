FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy inference requirements  
COPY requirements-inference.txt .
RUN pip install --no-cache-dir -r requirements-inference.txt

# OpenEnv layout: inference imports from backend/
COPY backend ./backend
COPY inference.py .
COPY openenv.yaml .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Runtime: set OPENAI_API_KEY, API_BASE_URL, MODEL_NAME (HF Space → Repository secrets).
# Container listens on the process default; HF Spaces maps port 7860 when applicable.
CMD ["python", "inference.py"]
