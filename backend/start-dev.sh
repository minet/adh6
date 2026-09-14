#!/bin/sh
set -eu

alembic upgrade head
exec uvicorn --port 8080 --host 0.0.0.0 main:application --reload
