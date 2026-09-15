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
COPY apps/worker-llm/pyproject.toml ./apps/worker-llm/

# Install external dependencies using uv cache mount
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-workspace --package worker-llm

# Copy application and shared source code
COPY shared/ ./shared/
COPY apps/worker-llm/ ./apps/worker-llm/

# Install project and local workspace packages
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --package worker-llm

# Runtime stage
FROM python:3.13-slim

# JRE required by opendataloader-pdf (runs a bundled JAR via subprocess)
RUN apt-get update && \
    apt-get install -y --no-install-recommends default-jre-headless && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app/apps/worker-llm

# Copy the pre-built virtual environment and source trees
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/shared /app/shared
COPY --from=builder /app/apps/worker-llm /app/apps/worker-llm

COPY docker/entrypoints/celery.sh /entrypoints/celery.sh
RUN chmod +x /entrypoints/celery.sh

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

ENV APP_MODULE=shared.celery_client
ENV QUEUE=llm_queue
ENV INCLUDE=worker
ENV CELERY_ARGS=--concurrency=1

CMD ["/entrypoints/celery.sh"]
