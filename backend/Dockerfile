# syntax=docker/dockerfile-upstream:master-labs

FROM python:3.11-alpine AS base

# Fetch OUIs database and pre-compile MIBs
FROM base AS prebuild
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
RUN apk add --no-cache --update wget \
    && wget -O - -o /dev/null http://standards-oui.ieee.org/oui.txt | grep '(hex)' | sed -E 's/\s*?\(hex\)\s+/\t/' > OUIs.txt
RUN adduser -s /bin/sh adh6 -h /home/adh6 -D
USER adh6
COPY backend/mibs.zip .
RUN uvx --from pysmi mibdump --mib-borrower="" --mib-source=mibs.zip CISCO-VLAN-MEMBERSHIP-MIB IF-MIB CISCO-MAC-AUTH-BYPASS-MIB IEEE8021-PAE-MIB

# Install production Python dependencies
FROM base AS build
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
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

# Extend prod venv with dev/test/lint dependencies
FROM build AS testbuild
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=backend/uv.lock,target=uv.lock \
    --mount=type=bind,source=backend/pyproject.toml,target=pyproject.toml \
    uv sync --locked --extra gunicorn --group dev

# Common runtime base shared by dev and prod
FROM base AS runtime
WORKDIR /app
RUN adduser -s /bin/sh adh6 -h /home/adh6 -D
COPY --from=prebuild /app/OUIs.txt .
COPY --from=prebuild --chown=adh6:adh6 /home/adh6/.pysnmp/ /home/adh6/.pysnmp/
COPY --from=build /app/.venv/ .venv/
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"
RUN apk add --no-cache --update \
    git \
    mariadb-connector-c
USER adh6
COPY backend/main.py backend/manage.py ./
COPY backend/migrations/ migrations/
COPY backend/adh6/ adh6/
COPY openapi/spec.yaml openapi/spec.yaml

FROM runtime AS dev
COPY backend/start-dev.sh .
CMD ["./start-dev.sh"]

FROM runtime AS prod
COPY backend/start.sh .
CMD ["./start.sh"]

# Debug stage (compose.debug-api.yaml)
FROM dev AS debug
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
ENV DEBUG=1
ENV LOG_LEVEL=DEBUG
USER root
RUN uv pip install debugpy
USER adh6
CMD ["python", "-Xfrozen_modules=off", "-m", "debugpy", "--wait-for-client", "--listen", "0.0.0.0:5678", "-m", "uvicorn", "--port", "8080", "--host", "0.0.0.0", "main:application", "--reload"]

# Test stage (CI/CD)
# Inherits the compiled prod .venv from build so mysqlclient/thrift are not recompiled.
# Dev-only packages (ruff, pyright, pytest…) are all pre-built wheels — no compiler needed.
# The .tox/ci env is pre-baked so CI jobs skip the uv-sync step entirely.
FROM base AS test
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
WORKDIR /app
ENV UV_LINK_MODE=copy
ENV UV_COMPILE_BYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"
COPY --from=prebuild /app/OUIs.txt .
COPY --from=prebuild /home/adh6/.pysnmp/ /root/.pysnmp/
COPY --from=build /app/.venv /app/.venv
COPY backend/pyproject.toml backend/uv.lock ./
# Extend the inherited prod venv with dev packages; pre-bake .tox/ci env
RUN --mount=type=cache,target=/var/cache/apk \
    --mount=type=cache,target=/root/.cache/uv \
    apk add --update \
    git \
    mariadb-connector-c \
    nodejs \
    && uv sync --locked --group dev \
    && uv run tox -e ci --notest
COPY openapi/spec.yaml openapi/spec.yaml
COPY backend/conftest.py backend/main.py backend/manage.py backend/start-dev.sh ./
COPY backend/migrations/ migrations/
COPY backend/adh6/ adh6/
COPY backend/test/ test/


