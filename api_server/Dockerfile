# syntax=docker/dockerfile-upstream:master-labs

# Pre-tasks
FROM python:3.11-alpine AS prebuild
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /adh6

# Get OUIs.txt
RUN apk add --no-cache --update wget \
    && wget -O - -o /dev/null http://standards-oui.ieee.org/oui.txt | grep '(hex)' | sed -E 's/\s*?\(hex\)\s+/\t/' > OUIs.txt

RUN adduser -s /bin/sh adh6 -h /home/adh6 -D
USER adh6

# Dump MIBs
COPY mibs.zip .
RUN uvx --from pysmi mibdump --mib-borrower="" --mib-source=mibs.zip CISCO-VLAN-MEMBERSHIP-MIB IF-MIB CISCO-MAC-AUTH-BYPASS-MIB IEEE8021-PAE-MIB


# Build
FROM python:3.11-alpine AS build
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV UV_LINK_MODE=copy
ENV UV_COMPILE_BYTECODE=1

WORKDIR /adh6
RUN --mount=type=cache,target=/var/cache/apk \
    --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    : \
    && apk add --no-cache --update git mariadb-dev build-base libffi-dev \
    && uv sync --no-dev --locked --extra gunicorn


# Production
FROM python:3.11-alpine
WORKDIR /adh6
RUN adduser -s /bin/bash adh6 -h /home/adh6 -D

COPY --from=prebuild /adh6/OUIs.txt .
COPY --from=prebuild --chown=adh6:adh6 /home/adh6/.pysnmp/ /home/adh6/.pysnmp/ 
COPY --from=build /adh6/.venv/ /adh6/.venv/

ENV PATH="/adh6/.venv/bin:$PATH"
RUN apk add --no-cache --update \ 
    git \
    mariadb-connector-c

USER adh6

WORKDIR /adh6/api_server
COPY . .

# Launch the app 
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornH11Worker", "-b", ":8080", "main:application"]
