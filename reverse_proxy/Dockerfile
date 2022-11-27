FROM alpine:3@sha256:8914eb54f968791faf6a8638949e480fef81e697984fba772b3976835194c6d4 AS certs
RUN apk add --no-cache --update openssl

# Make TLS self-signed certificate
RUN openssl genrsa -out /tmp/adh6.key 2048 \
  && openssl req -new -key /tmp/adh6.key -out /tmp/adh6.csr -subj "/C=FR/ST=Essonne/O=MiNET/CN=reverse_proxy" \
  && openssl x509 -req -days 365 -in /tmp/adh6.csr -signkey /tmp/adh6.key -out /tmp/adh6.crt

FROM nginx:alpine@sha256:455c39afebd4d98ef26dd70284aa86e6810b0485af5f4f222b19b89758cabf1e

ENV API_MEMBER_HOST=adh6_backend_member

COPY --from=certs /tmp/adh6.crt /etc/ssl/certs/
COPY --from=certs /tmp/adh6.key /etc/ssl/private/

