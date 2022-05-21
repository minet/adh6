###############################################################################
# 1st stage, build the app
###############################################################################
FROM node:18-alpine@sha256:f4d6916c5625853e81994b5cb53ad3eb27e5fec9451c579d298fee0c508fe621 as build
WORKDIR /adh6/frontend_angular

# Install packages
COPY package.json .
RUN yarn install --frozen-lockfile
# Copy source code
COPY . .
ENV NODE_OPTIONS=--openssl-legacy-provider

RUN yarn build

###############################################################################
# 2nd stage, host the app with nginx
###############################################################################
FROM nginx:alpine@sha256:5a0df7fb7c8c03e4158ae9974bfbd6a15da2bdfdeded4fb694367ec812325d31
EXPOSE 80
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /adh6/frontend_angular/dist/adh6/fr /usr/share/nginx/html/fr
COPY --from=build /adh6/frontend_angular/dist/adh6/en /usr/share/nginx/html/en
COPY --from=build /adh6/frontend_angular/src/assets /usr/share/nginx/html/assets

