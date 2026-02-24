# ============================
# 1. Base image
# ============================
FROM python:3.11-slim AS base

# Prevent Python from writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ============================
# 2. System dependencies
# ============================
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ============================
# 3. Working directory
# ============================
WORKDIR /app

# ============================
# 4. Install Python dependencies
# ============================
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ============================
# 5. Copy application code
# ============================
COPY . .

# ============================
# 6. Expose port for Twilio WS
# ============================
EXPOSE 8765

# ============================
# 7. Healthcheck (optional)
# ============================
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8765/health || exit 1

# ============================
# 8. Run the voice agent
# ============================
CMD ["python", "main.py"]
"]