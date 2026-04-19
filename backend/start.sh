#!/bin/sh
set -eu

gunicorn -b 0.0.0.0:8080 -w 4 main:application -k uvicorn.workers.UvicornWorker
