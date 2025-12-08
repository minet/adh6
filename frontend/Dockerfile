# syntax=docker/dockerfile-upstream:master-labs

FROM node:22-alpine AS prebuild
WORKDIR /app/frontend

# Install packages
ENV YARN_CACHE_FOLDER=/root/.yarn
RUN --mount=type=cache,target=/var/cache/apk \
    apk add python3 make g++ openssl

COPY frontend/src/assets ./src/assets
RUN yarn global add svgo \
    && cd ./src/assets \
    && svgo minet.svg minet-dark.svg adh6-logo.svg -o minet.min.svg minet-dark.min.svg adh6.min.svg

RUN --mount=type=cache,target=/root/.yarn \
    --mount=type=bind,source=frontend/package.json,target=package.json \
    --mount=type=bind,source=frontend/yarn.lock,target=yarn.lock \
    yarn install --frozen-lockfile


# TODO: remake for prod also
FROM prebuild AS prodbuild
COPY frontend/package.json frontend/angular.json frontend/tsconfig.json ./
COPY frontend/src src
RUN yarn build --configuration development
RUN yarn purgecss -css dist/adh6/browser/fr/*.css --content dist/adh6/browser/fr/index.html dist/adh6/browser/fr/*.js -o dist/adh6/browser/fr


# TODO: test
FROM nginx:alpine@sha256:455c39afebd4d98ef26dd70284aa86e6810b0485af5f4f222b19b89758cabf1e AS prod

COPY frontend/nginx/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=prodbuild /app/frontend/dist/adh6/browser/fr /usr/share/nginx/html/fr
COPY --from=prodbuild /app/frontend/dist/adh6/browser/en /usr/share/nginx/html/en
COPY --from=prodbuild /app/frontend/src/assets /usr/share/nginx/html/assets

# Set proper permissions and switch to the existing nginx user
RUN chown -R nginx:nginx /usr/share/nginx/html

USER nginx


FROM node:22-alpine AS dev

# Create a non-root user for Node.js
RUN addgroup -g 1001 -S nodeuser && \
    adduser -S -D -H -u 1001 -h /app -s /bin/sh -G nodeuser nodeuser

# Switch to non-root user early to avoid permission issues
USER nodeuser

WORKDIR /app
COPY --parents --exclude=frontend/src/assets frontend/src frontend/package.json frontend/angular.json frontend/tsconfig.json frontend/yarn.lock ./

WORKDIR /app/frontend
COPY --from=prebuild /app/frontend/node_modules ./node_modules
COPY --from=prebuild /app/frontend/src/assets ./src/assets

CMD yarn start:en --watch --host 0.0.0.0 --allowed-hosts true
