###############################################################################
# 1st stage: generate config files...
###############################################################################
FROM alpine:3@sha256:4edbd2beb5f78b1014028f4fbb99f3237d9561100b6881aabbf5acce2c4f9454 AS config
WORKDIR /tmp

ARG ADH6_URL="adh6.minet.net"
ARG SSO_OAUTH2="adh6.minet.net/api/oauth2"
ARG BYPASS_AUTH="false"

COPY src/app/config/auth.config.ts.template .
SHELL ["/bin/ash", "-o", "pipefail", "-c"]
RUN apk add --no-cache gettext \
  && cat auth.config.ts.template | envsubst | tee auth.config.ts


###############################################################################
# 2nd stage, build the app
###############################################################################
FROM node:18-alpine@sha256:f4d6916c5625853e81994b5cb53ad3eb27e5fec9451c579d298fee0c508fe621 as build
WORKDIR /adh6/frontend_angular

# Install packages
COPY package.json .
RUN yarn install --frozen-lockfile

# Copy source code
COPY . .

ENV NODE_OPTIONS=--openssl-legacy-provider

# Copy the generated config files.
COPY --from=config /tmp/auth.config.ts src/app/config/auth.config.ts

RUN yarn build

###############################################################################
# 3rd stage, host the app with nginx
###############################################################################
FROM nginx:alpine@sha256:5a0df7fb7c8c03e4158ae9974bfbd6a15da2bdfdeded4fb694367ec812325d31
EXPOSE 80
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /adh6/frontend_angular/dist/adh6/fr /usr/share/nginx/html/fr
COPY --from=build /adh6/frontend_angular/dist/adh6/en /usr/share/nginx/html/en
COPY --from=build /adh6/frontend_angular/src/assets /usr/share/nginx/html/assets

