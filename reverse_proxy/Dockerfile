FROM alpine:3.22.0 AS certs
RUN apk add --no-cache --update openssl

# Make TLS self-signed certificate
RUN openssl genrsa -out /tmp/adh6.key 2048 \
  && openssl req -new -key /tmp/adh6.key -out /tmp/adh6.csr -subj "/C=FR/ST=Essonne/O=MiNET/CN=reverse_proxy" \
  && openssl x509 -req -days 365 -in /tmp/adh6.csr -signkey /tmp/adh6.key -out /tmp/adh6.crt

FROM nginx:1.28.0 as with_certs

COPY --from=certs /tmp/adh6.crt /etc/ssl/certs/
COPY --from=certs /tmp/adh6.key /etc/ssl/private/

COPY reverse_proxy/default.conf.template /etc/nginx/templates/ 


# The production version does not use self signed certificates, it uses the external revproxy
FROM nginx:latest as production
COPY reverse_proxy/prod.conf.template /etc/nginx/templates/default.conf.template