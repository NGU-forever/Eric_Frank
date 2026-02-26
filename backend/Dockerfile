# syntax=docker/dockerfile:1

# ============================================================
# Stage 1 — Base Image
# ============================================================
FROM python:3.11-slim AS base

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# ============================================================
# Stage 2 — Install dependencies (cacheable layer)
# ============================================================
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ============================================================
# Stage 3 — Copy application code
# ============================================================
COPY . .

# Expose FastAPI port
EXPOSE 8000

# ============================================================
# Start FastAPI via uvicorn
# host=0.0.0.0 is REQUIRED for Docker container external access
# ============================================================
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
