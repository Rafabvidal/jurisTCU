# syntax=docker/dockerfile:1
FROM python:3.13-slim AS builder

# Install uv binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Copy workspace metadata for dependency resolution caching
COPY pyproject.toml uv.lock ./
COPY shared/pyproject.toml ./shared/
COPY apps/worker-scrapper/pyproject.toml ./apps/worker-scrapper/

# Install external dependencies using uv cache mount
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-workspace --package worker-scrapper

# Copy application and shared source code
COPY shared/ ./shared/
COPY apps/worker-scrapper/ ./apps/worker-scrapper/

# Install project and local workspace packages
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --package worker-scrapper

# Runtime stage
FROM python:3.13-slim

# System deps for Playwright and Chromium
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libnss3 libatk-bridge2.0-0 libxkbcommon0 libxcomposite1 \
        libxrandr2 libxdamage1 libgbm1 libasound2 libxshmfence1 \
        libgtk-3-0 libdrm2 libxfixes3 \
        libxcb1 libx11-6 libxrender1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app/apps/worker-scrapper

# Copy the pre-built virtual environment and source trees
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/shared /app/shared
COPY --from=builder /app/apps/worker-scrapper /app/apps/worker-scrapper

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Install Playwright browser binaries
RUN python -m playwright install --with-deps chromium

COPY docker/entrypoints/celery.sh /entrypoints/celery.sh
RUN chmod +x /entrypoints/celery.sh

ENV APP_MODULE=shared.celery_client
ENV QUEUE=scrapper_queue
ENV INCLUDE=pje_scraper.worker

CMD ["/entrypoints/celery.sh"]
