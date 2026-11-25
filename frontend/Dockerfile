# syntax=docker/dockerfile:1

FROM node:22-alpine@sha256:1314fb30ec37592d5845e5a160d522c0e680972aa534549940b8d73bde88481a AS prebuild
WORKDIR /app/frontend

# Install packages
ENV YARN_CACHE_FOLDER=/root/.yarn
RUN --mount=type=cache,target=/var/cache/apk,sharing=locked \
    apk add python3 make g++ openssl

RUN --mount=type=cache,target=/root/.yarn,sharing=locked \
    --mount=type=bind,source=frontend/package.json,target=package.json \
    --mount=type=bind,source=frontend/yarn.lock,target=yarn.lock \
    yarn install --frozen-lockfile

RUN --mount=type=cache,target=/root/.yarn,sharing=locked \
    yarn global add svgo@4.1.0

COPY frontend/src/assets ./src/assets
RUN cd ./src/assets \
    && svgo minet.svg minet-dark.svg adh67-logo.svg adh67-logo-dark.svg -o minet.min.svg minet-dark.min.svg adh6.min.svg adh6-dark.min.svg


FROM prebuild AS prodbuild
COPY frontend/package.json frontend/angular.json frontend/tsconfig.json ./
COPY frontend/src src
RUN ./node_modules/.bin/ng build --configuration production \
    && for locale in fr en; do \
      ./node_modules/.bin/purgecss --css dist/adh6/browser/$locale/*.css --content dist/adh6/browser/$locale/index.html dist/adh6/browser/$locale/*.js -o dist/adh6/browser/$locale || exit 1; \
    done


# CI test image: unit tests, ng lint and prettier run from /app/frontend
FROM prebuild AS test
COPY frontend/package.json frontend/angular.json frontend/tsconfig.json frontend/eslint.config.js frontend/.prettierrc frontend/.prettierignore ./
COPY frontend/src src
COPY frontend/test test


FROM nginx:alpine-slim@sha256:c293b28729906d97fa5302fce3bd79bd27a3ea9a5d9604e21c6ff0ebf14549fc AS prod

# Permissions set before copying the build so this layer stays cached
RUN mkdir -p /var/cache/nginx/client_temp \
    /var/cache/nginx/proxy_temp \
    /var/cache/nginx/fastcgi_temp \
    /var/cache/nginx/uwsgi_temp \
    /var/cache/nginx/scgi_temp \
    && chown -R nginx:nginx /usr/share/nginx/html /var/cache/nginx /var/log/nginx \
    && touch /var/run/nginx.pid \
    && chown nginx:nginx /var/run/nginx.pid

COPY frontend/nginx/nginx.conf /etc/nginx/conf.d/default.conf
COPY --chown=nginx:nginx --from=prodbuild /app/frontend/dist/adh6/browser/ /usr/share/nginx/html/

USER nginx


FROM node:22-alpine@sha256:1314fb30ec37592d5845e5a160d522c0e680972aa534549940b8d73bde88481a AS dev

# Create a non-root user for Node.js
RUN addgroup -g 1001 -S nodeuser && \
    adduser -S -D -H -u 1001 -h /app -s /bin/sh -G nodeuser nodeuser

# Switch to non-root user early to avoid permission issues
USER nodeuser

WORKDIR /app/frontend
COPY --from=prebuild /app/frontend/node_modules ./node_modules
COPY frontend/package.json frontend/angular.json frontend/tsconfig.json frontend/yarn.lock ./
# Sources possédées par nodeuser, sinon docker compose watch ne peut pas supprimer les fichiers
COPY --chown=nodeuser:nodeuser frontend/src ./src
COPY --chown=nodeuser:nodeuser --from=prebuild /app/frontend/src/assets ./src/assets

CMD ["sh", "-c", "trap 'kill \"$fr_pid\" \"$en_pid\" 2>/dev/null; wait' INT TERM EXIT; yarn start:fr --port 4200 --host 0.0.0.0 --allowed-hosts true & fr_pid=$!; yarn start:en --port 4201 --host 0.0.0.0 --allowed-hosts true & en_pid=$!; wait -n \"$fr_pid\" \"$en_pid\""]
