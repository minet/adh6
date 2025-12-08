# syntax=docker/dockerfile-upstream:master-labs

FROM python:3.11-alpine AS base

# Pre-tasks
FROM base AS prebuild
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app

# Get OUIs.txt
RUN apk add --no-cache --update wget \
    && wget -O - -o /dev/null http://standards-oui.ieee.org/oui.txt | grep '(hex)' | sed -E 's/\s*?\(hex\)\s+/\t/' > OUIs.txt

RUN adduser -s /bin/sh adh6 -h /home/adh6 -D
USER adh6

# Dump MIBs
COPY backend/mibs.zip .
RUN uvx --from pysmi mibdump --mib-borrower="" --mib-source=mibs.zip CISCO-VLAN-MEMBERSHIP-MIB IF-MIB CISCO-MAC-AUTH-BYPASS-MIB IEEE8021-PAE-MIB


# Build
FROM base AS build
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV UV_LINK_MODE=copy
ENV UV_COMPILE_BYTECODE=1

WORKDIR /app
RUN --mount=type=cache,target=/var/cache/apk \
    --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=backend/uv.lock,target=uv.lock \
    --mount=type=bind,source=backend/pyproject.toml,target=pyproject.toml \
    : \
    && apk add --no-cache --update git mariadb-dev build-base libffi-dev \
    && uv sync --no-dev --locked --extra gunicorn


# Production
FROM base AS dev

WORKDIR /app
RUN adduser -s /bin/sh adh6 -h /home/adh6 -D

COPY --from=prebuild /app/OUIs.txt ./backend/
COPY --from=prebuild --chown=adh6:adh6 /home/adh6/.pysnmp/ /home/adh6/.pysnmp/ 
COPY --from=build /app/.venv/ /app/.venv/

ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"
ENV FLASK_APP=manage:manager
RUN apk add --no-cache --update \ 
    git \
    mariadb-connector-c

USER adh6

COPY --parents backend/main.py backend/manage.py backend/start-dev.sh backend/migrations/ backend/adh6/ ./
COPY --parents openapi/spec.yaml ./backend

WORKDIR /app/backend
# Launch the app 
CMD ["./start-dev.sh"]

# Debug stage
FROM dev AS debug
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
ENV DEBUG=1
ENV LOG_LEVEL=DEBUG
ENV FLASK_APP=manage:manager
USER root
RUN uv pip install debugpy
USER adh6
RUN flask db upgrade head
CMD ["python", "-Xfrozen_modules=off", "-m", "debugpy", "--wait-for-client", "--listen", "0.0.0.0:5678", "-m", "uvicorn", "--port", "8080", "--host", "0.0.0.0", "main:application", "--reload"]
