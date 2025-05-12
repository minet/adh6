# syntax=docker/dockerfile-upstream:master-labs

# Pre-tasks: generate code from spec
FROM openapitools/openapi-generator-cli:v7.11.0 AS openapi-generate
WORKDIR /adh6
COPY spec.yaml ./
RUN /usr/local/bin/docker-entrypoint.sh generate -i ./spec.yaml -g typescript-angular -o "./output" --additional-properties=queryParamObjectFormat=key \
    && find ./output/api -type f -name "*.service.ts" -exec sed -i'' -e 's/private addToHttpParams(/private addToHttpParamsBad(/g' {} \; \
    && find ./output/api -type f -name "*.service.ts" -exec sed -i'' -e 's/addToHttpParamsRecursive/addToHttpParams/g' {} \;


FROM node:22-alpine AS prebuild
WORKDIR /adh6/frontend_angular

# Install packages
ENV YARN_CACHE_FOLDER=/root/.yarn
RUN --mount=type=cache,target=/var/cache/apk \
    apk add python3 make g++ openssl

COPY --parents src/assets ./
RUN yarn global add svgo \
    && cd ./src/assets \
    && svgo minet.svg minet-dark.svg adh6-logo.svg -o minet.min.svg minet-dark.min.svg adh6.min.svg

RUN --mount=type=cache,target=/root/.yarn \
    --mount=type=bind,source=package.json,target=package.json \
    --mount=type=bind,source=yarn.lock,target=yarn.lock \
    yarn install --frozen-lockfile


# TODO: remake for prod also
FROM prebuild AS prodbuild
COPY src src
RUN yarn build --configuration development
RUN yarn purgecss -css dist/adh6/fr/*.css --content dist/adh6/fr/index.html dist/adh6/fr/*.js -o dist/adh6/fr


FROM nginx:alpine@sha256:455c39afebd4d98ef26dd70284aa86e6810b0485af5f4f222b19b89758cabf1e AS prod

COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=prodbuild /adh6/frontend_angular/dist/adh6/fr /usr/share/nginx/html/fr
COPY --from=prodbuild /adh6/frontend_angular/dist/adh6/en /usr/share/nginx/html/en
COPY --from=prodbuild /adh6/frontend_angular/src/assets /usr/share/nginx/html/assets


FROM node:22-alpine AS dev
WORKDIR /adh6/frontend_angular

COPY --parents --exclude=src/assets src package.json angular.json tsconfig.json ./
COPY --from=prebuild --parents /adh6/frontend_angular/node_modules /adh6/frontend_angular/src/assets /
COPY --from=openapi-generate /adh6/output /adh6/frontend_angular/src/app/api

CMD yarn start:en --watch --host 0.0.0.0 --disable-host-check
