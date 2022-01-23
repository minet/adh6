###############################################################################
# 1st stage: generate config files...
###############################################################################
FROM alpine:latest AS config
RUN apk add gettext && apk update && apk upgrade
WORKDIR /tmp

ARG OAUTH2_BASE_PATH="my-sso/oauth2.0"
ARG AUTH_CONSENT_ADDRESS="my-app/consent"
ARG DATABASE_HOST="localhost"
ARG DATABASE_PORT="1234"
ARG DATABASE_USERNAME="my_db_username"
ARG DATABASE_PASSWORD="my_db_password"
ARG DATABASE_DB_NAME="adh6"
ARG GITLAB_ACCESS_TOKEN="token"

COPY api_server/config/CONFIGURATION.template.py .
RUN cat CONFIGURATION.template.py | envsubst | tee CONFIGURATION.py

###############################################################################
# 2nd stage, generate certificats
###############################################################################
FROM alpine:latest AS certs
RUN apk add --update openssl
RUN openssl genrsa -out /tmp/adh6.key 2048 \
    && openssl req -new -key /tmp/adh6.key -out /tmp/adh6.csr -subj "/C=FR/ST=Essonne/O=MiNET/CN=frontend" \
    && openssl x509 -req -days 365 -in /tmp/adh6.csr -signkey /tmp/adh6.key -out /tmp/adh6.crt


FROM python:3.9-slim
EXPOSE 443

COPY --from=certs /tmp/adh6.crt /etc/ssl/certs/
COPY --from=certs /tmp/adh6.key /etc/ssl/private/

# Install dependencies
RUN apt update \
    && apt install -y \
    build-essential \
    python3-dev \
    libpcre3 \
    libpcre3-dev \
    libssl-dev \
    libmariadb-dev \
    git \
    wget \
    && useradd uwsgi

WORKDIR /adh6/api_server

# Download the latest OUI list from the IEEE
RUN wget -O - -o /dev/null http://standards-oui.ieee.org/oui.txt | grep '(hex)' | sed -E 's/\s*?\(hex\)\s+/\t/' > OUIs.txt

# Install python requirements
COPY api_server/requirements.txt ./
RUN pip3 install -r ./requirements.txt

# Build all MIBs required by pysnmp
COPY api_server/mibs.zip ./
RUN mibdump.py --mib-borrower="" --mib-source=mibs.zip CISCO-VLAN-MEMBERSHIP-MIB IF-MIB CISCO-MAC-AUTH-BYPASS-MIB IEEE8021-PAE-MIB
RUN chmod 755 /root
RUN chown -R uwsgi:www-data /root/.pysnmp

# Copy source files
COPY ./openapi/spec.yaml ../openapi/
COPY ./api_server ./
COPY --from=config /tmp/CONFIGURATION.py config/

# Launch the app 
CMD ["uwsgi", "--ini", "uwsgi.ini"]
