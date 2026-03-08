#!/bin/sh
set -eu

# Legacy Flask migration path is disabled by default for FastAPI runtime.
# Set RUN_MIGRATIONS=1 to opt in (best effort).
if [ "${RUN_MIGRATIONS:-0}" = "1" ]; then
	if command -v flask >/dev/null 2>&1; then
		FLASK_APP=manage:manager flask db upgrade head || true
	else
		echo "[startup] flask command not found, skipping migrations"
	fi
fi

# start the application
# uvicorn --port 8080 --host 0.0.0.0 main:application
gunicorn -b 0.0.0.0:8080 -w 4 main:application -k uvicorn.workers.UvicornWorker
