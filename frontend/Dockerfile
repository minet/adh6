FROM node:22-alpine AS prebuild
WORKDIR /app/frontend

# Install packages
ENV YARN_CACHE_FOLDER=/root/.yarn
RUN --mount=type=cache,target=/var/cache/apk \
    apk add python3 make g++ openssl

COPY frontend/src/assets ./src/assets
RUN yarn global add svgo \
    && cd ./src/assets \
    && svgo minet.svg minet-dark.svg adh6-logo.svg adh6-logo-dark.svg -o minet.min.svg minet-dark.min.svg adh6.min.svg adh6-dark.min.svg

RUN --mount=type=cache,target=/root/.yarn \
    --mount=type=bind,source=frontend/package.json,target=package.json \
    --mount=type=bind,source=frontend/yarn.lock,target=yarn.lock \
    yarn install --frozen-lockfile


# TODO: remake for prod also
FROM prebuild AS prodbuild
COPY frontend/package.json frontend/angular.json frontend/tsconfig.json ./
COPY frontend/src src
RUN ./node_modules/.bin/ng build --configuration production \
    && for locale in fr en; do \
      ./node_modules/.bin/purgecss -css dist/adh6/browser/$locale/*.css --content dist/adh6/browser/$locale/index.html dist/adh6/browser/$locale/*.js -o dist/adh6/browser/$locale; \
    done


# TODO: test
FROM nginx:alpine@sha256:455c39afebd4d98ef26dd70284aa86e6810b0485af5f4f222b19b89758cabf1e AS prod

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
COPY --chown=nginx:nginx --from=prodbuild /app/frontend/src/assets /usr/share/nginx/html/assets

USER nginx


FROM node:22-alpine AS dev

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

CMD yarn start:en --watch --host 0.0.0.0 --allowed-hosts true
