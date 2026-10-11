# Use official lightweight Python 3.11 Debian slim base image
FROM python:3.11-slim

LABEL maintainer="SelfHeal Team"
LABEL description="Self-Healing E2E Test System Engine and Demo Shop"

# Environment configuration
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    HOST=0.0.0.0 \
    PORT=5000 \
    DEMO_BASE_URL=http://127.0.0.1:5000 \
    HEADLESS=true \
    PLAYWRIGHT_NO_SANDBOX=true

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Install Playwright Chromium browser and OS dependencies
RUN playwright install --with-deps chromium

# Create non-root user and ensure permissions
RUN useradd -m -u 1000 appuser \
    && mkdir -p /ms-playwright /app/runs \
    && chown -R appuser:appuser /ms-playwright /app

# Copy application source code
COPY . .

# Normalize line endings and permissions for entrypoint
RUN sed -i 's/\r$//' /app/entrypoint.sh \
    && chmod +x /app/entrypoint.sh \
    && chown -R appuser:appuser /app

# Run as unprivileged user
USER appuser

# Expose Demo Shop HTTP port
EXPOSE 5000

# Health check endpoint verification
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health')" || exit 1

# Configure entrypoint and default command
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "-m", "demo_app.app"]
