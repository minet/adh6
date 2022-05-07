###############################################################################
# 1st stage: generate config files...
###############################################################################
FROM alpine:latest AS config
RUN apk add gettext && apk update && apk upgrade
WORKDIR /tmp

ARG ADH6_URL="adh6.minet.net"
ARG SSO_OAUTH2="adh6.minet.net/api/oauth2"
ARG BYPASS_AUTH="false"

COPY src/app/config/auth.config.ts.template .

RUN cat auth.config.ts.template | envsubst | tee auth.config.ts


###############################################################################
# 2nd stage, build the app
###############################################################################
FROM node:16-alpine as build
WORKDIR /adh6/frontend_angular

# Install angular system-wide
RUN NG_CLI_ANALYTICS=ci npm install -g @angular/cli@latest

# Install packages
COPY package.json .
RUN yarn install

# Copy source code
COPY . .
# Copy the generated config files.
COPY --from=config /tmp/auth.config.ts src/app/config/auth.config.ts

RUN yarn build

###############################################################################
# 3rd stage, host the app with nginx
###############################################################################
FROM nginx:alpine
EXPOSE 80
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /adh6/frontend_angular/dist/adh6/fr /usr/share/nginx/html/fr
COPY --from=build /adh6/frontend_angular/dist/adh6/en /usr/share/nginx/html/en
COPY --from=build /adh6/frontend_angular/src/assets /usr/share/nginx/html/assets

