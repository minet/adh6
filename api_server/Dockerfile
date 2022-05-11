###############################################################################
# 1st stage: generate config files...
###############################################################################
FROM alpine:3@sha256:4edbd2beb5f78b1014028f4fbb99f3237d9561100b6881aabbf5acce2c4f9454 AS config
WORKDIR /tmp

ARG OAUTH2_BASE_PATH="my-sso/oauth2.0"
ARG AUTH_CONSENT_ADDRESS="my-app/consent"
ARG DATABASE_HOST="localhost"
ARG DATABASE_PORT="1234"
ARG DATABASE_USERNAME="my_db_username"
ARG DATABASE_PASSWORD="my_db_password"
ARG DATABASE_DB_NAME="adh6"
ARG GITLAB_ACCESS_TOKEN="token"

COPY api_server/config/.env.template .
SHELL ["/bin/ash", "-o", "pipefail", "-c"]
RUN apk add --no-cache gettext \ 
  && cat .env.template | envsubst | tee .env

###############################################################################
# 2nd stage, generate certificats
###############################################################################
FROM alpine:3@sha256:4edbd2beb5f78b1014028f4fbb99f3237d9561100b6881aabbf5acce2c4f9454 AS certs
RUN apk add --no-cache --update openssl
RUN openssl genrsa -out /tmp/adh6.key 2048 \
  && openssl req -new -key /tmp/adh6.key -out /tmp/adh6.csr -subj "/C=FR/ST=Essonne/O=MiNET/CN=frontend" \
  && openssl x509 -req -days 365 -in /tmp/adh6.csr -signkey /tmp/adh6.key -out /tmp/adh6.crt

###############################################################################
# 3nd stage, get OUI.txt
###############################################################################
FROM alpine:3@sha256:4edbd2beb5f78b1014028f4fbb99f3237d9561100b6881aabbf5acce2c4f9454 AS oui
WORKDIR /tmp
SHELL ["/bin/ash", "-o", "pipefail", "-c"]
RUN apk add --no-cache --update wget \
  && wget -O - -o /dev/null http://standards-oui.ieee.org/oui.txt | grep '(hex)' | sed -E 's/\s*?\(hex\)\s+/\t/' > OUIs.txt

###############################################################################
# 4nd stage, deploy the application
###############################################################################
FROM python:3.9-slim@sha256:ba3b77ddbc953cdb8d998b2052088d4af4b8805805e5b01975a05af4e19855ea
EXPOSE 443

WORKDIR /adh6/api_server

COPY --from=certs /tmp/adh6.crt /tmp/
COPY --from=certs /tmp/adh6.key /tmp/
COPY --from=oui /tmp/OUIs.txt .

# Download the latest OUI list from the IEEE
RUN chmod o+r /tmp/adh6.crt /tmp/adh6.key

# Install dependencies
RUN apt-get update \
  && apt-get --no-install-recommends install -y \
  build-essential \
  python3-dev \
  libpcre3 \
  libpcre3-dev \
  libssl-dev \
  libmariadb-dev \
  git \
  wget \
  && useradd -ms /bin/bash uwsgi \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Install python requirements
COPY api_server/requirements.txt ./
RUN pip3 install --no-cache-dir -r ./requirements.txt
USER uwsgi
# Build all MIBs required by pysnmp
COPY api_server/mibs.zip .
RUN mibdump.py --mib-borrower="" --mib-source=mibs.zip CISCO-VLAN-MEMBERSHIP-MIB IF-MIB CISCO-MAC-AUTH-BYPASS-MIB IEEE8021-PAE-MIB

# Copy source files
COPY ./openapi/spec.yaml ../openapi/
COPY ./api_server ./
COPY --from=config /tmp/.env config/

# Launch the app 
CMD ["uwsgi", "--ini", "uwsgi.ini"]
