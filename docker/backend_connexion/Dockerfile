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
COPY api_server/mibs.zip .
RUN uvx --from pysmi mibdump --mib-borrower="" --mib-source=mibs.zip CISCO-VLAN-MEMBERSHIP-MIB IF-MIB CISCO-MAC-AUTH-BYPASS-MIB IEEE8021-PAE-MIB

# Pre-tasks: generate code from spec
FROM openapitools/openapi-generator-cli:v7.12.0 AS openapi-generate
WORKDIR /app
COPY openapi/spec.yaml ./
RUN /usr/local/bin/docker-entrypoint.sh generate -i ./spec.yaml -g python-flask -o ./raw_output --additional-properties packageName=adh6 --additional-properties=modelPackage=entity \
    && mkdir  ./output \
    && cp -r ./raw_output/adh6/entity/ ./output/entity/ \
    && cp ./raw_output/adh6/typing_utils.py ./output/ \
    && cp ./raw_output/adh6/util.py ./output/ \
    && sed -i'' -e 's/result\[attr\]/result\[self.attribute_map\[attr\]\]/g' ./output/entity/base_model.py


# Build
FROM base AS build
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV UV_LINK_MODE=copy
ENV UV_COMPILE_BYTECODE=1

WORKDIR /app
RUN --mount=type=cache,target=/var/cache/apk \
    --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=api_server/uv.lock,target=uv.lock \
    --mount=type=bind,source=api_server/pyproject.toml,target=pyproject.toml \
    : \
    && apk add --no-cache --update git mariadb-dev build-base libffi-dev \
    && uv sync --no-dev --locked --extra gunicorn


# Production
FROM base AS dev

WORKDIR /app
RUN adduser -s /bin/sh adh6 -h /home/adh6 -D

COPY --from=prebuild /app/OUIs.txt ./api_server/
COPY --from=prebuild --chown=adh6:adh6 /home/adh6/.pysnmp/ /home/adh6/.pysnmp/ 
COPY --from=build /app/.venv/ /app/.venv/
COPY --from=openapi-generate /app/output/ ./api_server/adh6

ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"
RUN apk add --no-cache --update \ 
    git \
    mariadb-connector-c

USER adh6

COPY --parents api_server/main.py api_server/manage.py api_server/start-dev.sh api_server/migrations/ api_server/adh6/ ./
COPY --parents openapi/spec.yaml ./api_server

WORKDIR /app/api_server
# Launch the app 
CMD ["./start-dev.sh"]
