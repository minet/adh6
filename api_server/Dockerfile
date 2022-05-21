###############################################################################
# 1st stage, get OUI.txt
###############################################################################
FROM alpine:3@sha256:4edbd2beb5f78b1014028f4fbb99f3237d9561100b6881aabbf5acce2c4f9454 AS oui
WORKDIR /tmp
SHELL ["/bin/ash", "-o", "pipefail", "-c"]
RUN apk add --no-cache --update wget \
  && wget -O - -o /dev/null http://standards-oui.ieee.org/oui.txt | grep '(hex)' | sed -E 's/\s*?\(hex\)\s+/\t/' > OUIs.txt

FROM python:3.9-alpine@sha256:602cd35ea12a7abc69078f447be06634700bdea7a2642712f8d21cfc35792df0 AS base
WORKDIR /wheels
# Install dependencies
RUN apk add --no-cache --update git

###############################################################################
# 2nd stage, get wheel files
###############################################################################
FROM base AS wheel
# Install dependencies
RUN apk add --no-cache --update \
  mariadb-dev \
  build-base \
  libffi-dev

WORKDIR /wheels

# Install python requirements
COPY requirements.txt .
RUN pip install -U pip \
  && pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

###############################################################################
# 3rd stage, deploy the application
###############################################################################
FROM base
RUN apk add --no-cache --update mariadb-connector-c

EXPOSE 443
WORKDIR /adh6/api_server

RUN adduser -s /bin/bash uwsgi -h /home/uwsgi -D
COPY --from=wheel /wheels /wheels
RUN chown uwsgi:uwsgi -R /wheels
RUN pip install --no-cache-dir -U pip \
  && pip install -r /wheels/requirements.txt \
  -f /wheels

USER root 
RUN rm -rf /wheels

USER uwsgi
COPY --from=oui /tmp/OUIs.txt .

# Build all MIBs required by pysnmp
COPY mibs.zip .
RUN mibdump.py --mib-borrower="" --mib-source=mibs.zip CISCO-VLAN-MEMBERSHIP-MIB IF-MIB CISCO-MAC-AUTH-BYPASS-MIB IEEE8021-PAE-MIB

# Copy source files
COPY . .

# Launch the app 
CMD ["uwsgi", "--ini", "uwsgi.ini"]
