#!/bin/sh
set -eu

alembic upgrade head
exec gunicorn -b 0.0.0.0:8080 -w 4 main:application -k uvicorn.workers.UvicornWorker
