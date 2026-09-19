# syntax=docker/dockerfile:1

FROM node:22-alpine@sha256:c610fcdfb1d5b4740dd70c284ed3cb16bb857e0f7166196e36a5501df7a3aa32 AS prebuild
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
      ./node_modules/.bin/purgecss -css dist/adh6/browser/$locale/*.css --content dist/adh6/browser/$locale/index.html dist/adh6/browser/$locale/*.js -o dist/adh6/browser/$locale; \
    done


FROM nginx:alpine-slim@sha256:688240d46d75f73c320b93657b5fc1d3500589fc11fd122eefdfa9e8d4d7dbc7 AS prod

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


FROM node:22-alpine@sha256:c610fcdfb1d5b4740dd70c284ed3cb16bb857e0f7166196e36a5501df7a3aa32 AS dev

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
