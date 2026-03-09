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
# Bakes uv cache into the image so tox-uv can create envs without network access
FROM base AS test
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
WORKDIR /app
ENV UV_LINK_MODE=copy
ENV UV_COMPILE_BYTECODE=1
ENV UV_CACHE_DIR=/app/.uv-cache
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"
COPY --from=prebuild /app/OUIs.txt .
COPY --from=prebuild /home/adh6/.pysnmp/ /root/.pysnmp/
COPY backend/pyproject.toml backend/uv.lock ./
# Install build deps + sync all dev groups (bakes uv cache into image layer for tox-uv)
RUN apk add --no-cache --update \
    git \
    mariadb-connector-c \
    mariadb-dev \
    build-base \
    libffi-dev \
    && uv sync --locked --group dev
COPY backend/conftest.py backend/main.py backend/manage.py backend/start-dev.sh ./
COPY backend/migrations/ migrations/
COPY backend/adh6/ adh6/
COPY backend/test/ test/
COPY openapi/spec.yaml openapi/spec.yaml

# Pyright stage - python:3.11-alpine base + npm Node.js for pyright-to-gitlab-ci
FROM base AS pyright-check
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
WORKDIR /app
ENV UV_LINK_MODE=copy
ENV UV_COMPILE_BYTECODE=1
ENV UV_CACHE_DIR=/app/.uv-cache
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"
COPY --from=prebuild /app/OUIs.txt .
COPY --from=prebuild /home/adh6/.pysnmp/ /root/.pysnmp/
COPY backend/pyproject.toml backend/uv.lock ./
RUN apk add --no-cache --update \
    git \
    mariadb-connector-c \
    mariadb-dev \
    build-base \
    libffi-dev \
    nodejs \
    npm \
    && uv sync --locked --group dev \
    && npm install -g pyright pyright-to-gitlab-ci
COPY backend/conftest.py backend/main.py backend/manage.py backend/start-dev.sh ./
COPY backend/migrations/ migrations/
COPY backend/adh6/ adh6/
COPY backend/test/ test/
COPY openapi/spec.yaml openapi/spec.yaml
