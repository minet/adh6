###############################################################################
# 1st stage, build the app
###############################################################################
FROM node:18-alpine@sha256:9eff44230b2fdcca57a73b8f908c8029e72d24dd05cac5339c79d3dedf6b208b as build
WORKDIR /adh6/frontend_angular

# Install packages
COPY package.json .
RUN yarn install --frozen-lockfile
# Copy source code
COPY . .
ENV NODE_OPTIONS=--openssl-legacy-provider

RUN yarn build --configuration development
RUN yarn purgecss -css dist/adh6/fr/*.css --content dist/adh6/fr/index.html dist/adh6/fr/*.js -o dist/adh6/fr

###############################################################################
# 2nd stage, host the app with nginx
###############################################################################
FROM nginx:alpine@sha256:455c39afebd4d98ef26dd70284aa86e6810b0485af5f4f222b19b89758cabf1e
EXPOSE 80
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /adh6/frontend_angular/dist/adh6/fr /usr/share/nginx/html/fr
COPY --from=build /adh6/frontend_angular/dist/adh6/en /usr/share/nginx/html/en
COPY --from=build /adh6/frontend_angular/src/assets /usr/share/nginx/html/assets

