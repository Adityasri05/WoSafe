# ============================================
# WoSafe Backend — Production Dockerfile
# ============================================
# Multi-stage build for minimal production image

# ── Stage 1: Builder ────────────────────────
FROM python:3.13-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir --prefix=/install .

# ── Stage 2: Production ────────────────────
FROM python:3.13-slim AS production

LABEL maintainer="WoSafe Team"
LABEL description="WoSafe AI-Powered Women's Safety Platform Backend"

# Security: run as non-root
RUN groupadd -r wosafe && useradd -r -g wosafe -d /app -s /sbin/nologin wosafe

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Set ownership
RUN chown -R wosafe:wosafe /app

USER wosafe

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Expose port
EXPOSE 8000

# Run with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--loop", "uvloop", "--http", "httptools"]
