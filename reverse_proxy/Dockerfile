FROM alpine:3@sha256:4edbd2beb5f78b1014028f4fbb99f3237d9561100b6881aabbf5acce2c4f9454 AS certs
RUN apk add --no-cache --update openssl

# Make TLS self-signed certificate
RUN openssl genrsa -out /tmp/adh6.key 2048 \
  && openssl req -new -key /tmp/adh6.key -out /tmp/adh6.csr -subj "/C=FR/ST=Essonne/O=MiNET/CN=reverse_proxy" \
  && openssl x509 -req -days 365 -in /tmp/adh6.csr -signkey /tmp/adh6.key -out /tmp/adh6.crt

FROM nginx:alpine@sha256:5a0df7fb7c8c03e4158ae9974bfbd6a15da2bdfdeded4fb694367ec812325d31

COPY --from=certs /tmp/adh6.crt /etc/ssl/certs/
COPY --from=certs /tmp/adh6.key /etc/ssl/private/

