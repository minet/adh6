# syntax=docker/dockerfile-upstream:master-labs

FROM node:22-alpine AS prebuild
WORKDIR /adh6/frontend_angular

# Install packages
ENV YARN_CACHE_FOLDER=/root/.yarn
RUN --mount=type=cache,target=/var/cache/apk \
    --mount=type=cache,target=/root/.yarn \
    --mount=type=bind,source=package.json,target=package.json \
    --mount=type=bind,source=yarn.lock,target=yarn.lock \
    apk add python3 make g++ openssl \
    && yarn install --frozen-lockfile


FROM prebuild AS devbuild
RUN --mount=type=cache,target=/var/cache/apk \
    apk add openssl

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

COPY --from=devbuild --parents /adh6/frontend_angular/node_modules /
COPY --parents src package.json angular.json tsconfig.json ./

# CMD ls
CMD yarn start:en --watch --host 0.0.0.0 --disable-host-check
