# syntax=docker/dockerfile-upstream:master-labs

# Pre-tasks: generate code from spec
FROM openapitools/openapi-generator-cli:v7.11.0 AS openapi-generate
WORKDIR /app
COPY openapi/spec.yaml ./
RUN /usr/local/bin/docker-entrypoint.sh generate -i ./spec.yaml -g typescript-angular -o "./output" --additional-properties=queryParamObjectFormat=key \
    && find ./output/api -type f -name "*.service.ts" -exec sed -i'' -e 's/private addToHttpParams(/private addToHttpParamsBad(/g' {} \; \
    && find ./output/api -type f -name "*.service.ts" -exec sed -i'' -e 's/addToHttpParamsRecursive/addToHttpParams/g' {} \;


FROM node:22-alpine AS prebuild
WORKDIR /app/frontend_angular

# Install packages
ENV YARN_CACHE_FOLDER=/root/.yarn
RUN --mount=type=cache,target=/var/cache/apk \
    apk add python3 make g++ openssl

COPY frontend_angular/src/assets ./src/assets
RUN yarn global add svgo \
    && cd ./src/assets \
    && svgo minet.svg minet-dark.svg adh6-logo.svg -o minet.min.svg minet-dark.min.svg adh6.min.svg

RUN --mount=type=cache,target=/root/.yarn \
    --mount=type=bind,source=frontend_angular/package.json,target=package.json \
    --mount=type=bind,source=frontend_angular/yarn.lock,target=yarn.lock \
    yarn install --frozen-lockfile


# TODO: remake for prod also
FROM prebuild AS prodbuild
COPY frontend_angular/package.json frontend_angular/angular.json frontend_angular/tsconfig.json ./
COPY frontend_angular/src src
RUN yarn build --configuration development
RUN yarn purgecss -css dist/adh6/browser/fr/*.css --content dist/adh6/browser/fr/index.html dist/adh6/browser/fr/*.js -o dist/adh6/browser/fr


# TODO: test
FROM nginx:alpine@sha256:455c39afebd4d98ef26dd70284aa86e6810b0485af5f4f222b19b89758cabf1e AS prod

COPY frontend_angular/nginx/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=prodbuild /app/frontend_angular/dist/adh6/browser/fr /usr/share/nginx/html/fr
COPY --from=prodbuild /app/frontend_angular/dist/adh6/browser/en /usr/share/nginx/html/en
COPY --from=prodbuild /app/frontend_angular/src/assets /usr/share/nginx/html/assets

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
COPY --parents --exclude=frontend_angular/src/assets frontend_angular/src frontend_angular/package.json frontend_angular/angular.json frontend_angular/tsconfig.json frontend_angular/yarn.lock ./

WORKDIR /app/frontend_angular
COPY --from=prebuild /app/frontend_angular/node_modules ./node_modules
COPY --from=prebuild /app/frontend_angular/src/assets ./src/assets
COPY --from=openapi-generate /app/output ./src/app/api

CMD yarn start:en --watch --host 0.0.0.0 --allowed-hosts true
