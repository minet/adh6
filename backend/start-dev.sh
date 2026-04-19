#!/bin/sh
set -eu

uvicorn --port 8080 --host 0.0.0.0 main:application --reload
