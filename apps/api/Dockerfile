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
COPY apps/api/pyproject.toml ./apps/api/

# Install external dependencies excluding local workspace members
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-workspace --package api

# Copy application and shared source code
COPY shared/ ./shared/
COPY apps/api/ ./apps/api/

# Install project and local workspace packages
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --package api

# Runtime stage
FROM python:3.13-slim

WORKDIR /app/apps/api

# Copy the pre-built virtual environment and source trees
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/shared /app/shared
COPY --from=builder /app/apps/api /app/apps/api

COPY docker/entrypoints/api.sh /entrypoints/api.sh
RUN chmod +x /entrypoints/api.sh

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

ENTRYPOINT [ "/entrypoints/api.sh" ]
