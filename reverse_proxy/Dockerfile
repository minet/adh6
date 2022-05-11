FROM alpine:3@sha256:4edbd2beb5f78b1014028f4fbb99f3237d9561100b6881aabbf5acce2c4f9454 AS config

WORKDIR /tmp

ARG ADH6_URL="adh6.minet.net"

ARG API_HOST=""
ARG API_PORT=""

ARG FRONTEND_HOST=""
ARG FRONTEND_PORT=""

COPY adh6.template.conf .
SHELL ["/bin/ash", "-o", "pipefail", "-c"]
RUN apk add --no-cache gettext \
  && cat adh6.template.conf | envsubst '${ADH6_URL} ${API_HOST} ${API_PORT} ${FRONTEND_HOST} ${FRONTEND_PORT}' | tee adh6.conf


FROM alpine:3@sha256:4edbd2beb5f78b1014028f4fbb99f3237d9561100b6881aabbf5acce2c4f9454 AS certs
RUN apk add --no-cache --update openssl

# Make TLS self-signed certificate
RUN openssl genrsa -out /tmp/adh6.key 2048 \
  && openssl req -new -key /tmp/adh6.key -out /tmp/adh6.csr -subj "/C=FR/ST=Essonne/O=MiNET/CN=reverse_proxy" \
  && openssl x509 -req -days 365 -in /tmp/adh6.csr -signkey /tmp/adh6.key -out /tmp/adh6.crt

FROM nginx:alpine@sha256:5a0df7fb7c8c03e4158ae9974bfbd6a15da2bdfdeded4fb694367ec812325d31

COPY --from=certs /tmp/adh6.crt /etc/ssl/certs/
COPY --from=certs /tmp/adh6.key /etc/ssl/private/

COPY --from=config /tmp/adh6.conf /etc/nginx/conf.d/adh6.conf

RUN rm /etc/nginx/conf.d/default.conf

