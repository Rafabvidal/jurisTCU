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
COPY apps/search-notifier/pyproject.toml ./apps/search-notifier/

# Install external dependencies using uv cache mount
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-workspace --package search-notifier

# Copy application and shared source code
COPY shared/ ./shared/
COPY apps/search-notifier/ ./apps/search-notifier/

# Install project and local workspace packages
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --package search-notifier

# Runtime stage
FROM python:3.13-slim

WORKDIR /app/apps/search-notifier

# Install supercronic (cron runner for containers)
ADD --chmod=755 https://github.com/aptible/supercronic/releases/download/v0.2.30/supercronic-linux-amd64 /usr/local/bin/supercronic

# Install crontab
COPY docker/cron/search_notifier.crontab /etc/cron/search_notifier.crontab

# Copy the pre-built virtual environment and source trees
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/shared /app/shared
COPY --from=builder /app/apps/search-notifier /app/apps/search-notifier

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

CMD ["supercronic", "/etc/cron/search_notifier.crontab"]
