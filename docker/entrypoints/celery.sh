#!/usr/bin/env bash

# Common entrypoint for Celery workers.
# Required env:
#   APP_MODULE   - Python module containing the Celery app (e.g., shared.celery_client)
# Optional env:
#   CELERY_CMD   - command to run (default: worker)
#   CELERY_ARGS  - extra args appended verbatim
#   QUEUE        - queue name to consume (becomes -Q $QUEUE)
#   INCLUDE      - module(s) to import on boot so @app.task decorators register (becomes --include=$INCLUDE)

set -euo pipefail

CELERY_APP="${APP_MODULE}"
CMD="${CELERY_CMD:-worker}"
ARGS="${CELERY_ARGS:-}"

if [ -n "${QUEUE:-}" ]; then
  ARGS="$ARGS -Q $QUEUE"
fi
if [ -n "${INCLUDE:-}" ]; then
  ARGS="$ARGS --include=$INCLUDE"
fi

exec celery -A "$CELERY_APP" "$CMD" $ARGS
