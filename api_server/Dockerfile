###############################################################################
# 1st stage, get OUI.txt
###############################################################################
FROM alpine:3@sha256:8914eb54f968791faf6a8638949e480fef81e697984fba772b3976835194c6d4 AS oui
WORKDIR /tmp
RUN apk add --no-cache --update wget \
  && wget -O - -o /dev/null http://standards-oui.ieee.org/oui.txt | grep '(hex)' | sed -E 's/\s*?\(hex\)\s+/\t/' > OUIs.txt

###############################################################################
# 2nd stage, get wheel files
###############################################################################
FROM python:3.12-alpine AS wheel
WORKDIR /wheels
# Install dependencies
RUN apk add --no-cache --update \
  git \
  mariadb-dev \
  build-base \
  libffi-dev

WORKDIR /wheels

# Install python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -U pip \
  && pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

###############################################################################
# 3rd stage, deploy the application
###############################################################################
FROM python:3.12-alpine
RUN apk add --no-cache --update \ 
  git \
  mariadb-connector-c

EXPOSE 443
WORKDIR /adh6/api_server

RUN adduser -s /bin/bash uwsgi -h /home/uwsgi -D
COPY --from=wheel /wheels /wheels
RUN pip install gunicorn
RUN chown uwsgi:uwsgi -R /wheels
RUN pip install --no-cache-dir -U pip \
  && pip install -r /wheels/requirements.txt \
  -f /wheels

USER root 
RUN rm -rf /wheels

USER uwsgi
COPY --from=oui /tmp/OUIs.txt .

# Build all MIBs required by pysnmp
# MIB is a text file that describes the structure of a SNMP device in a human-readable format
# SNMP is the protocol used to manage and monitor network devices 
# CISCO-VLAN-MEMBERSHIP-MIB: Describes the VLAN membership of a device
# IF-MIB: Describes the interfaces of a device
# CISCO-MAC-AUTH-BYPASS-MIB: Describes the MAC authentication bypass of a device
# IEEE8021-PAE-MIB: Describes the 802.1X port access entity of a device
# mibdump.py is a tool provided by pysnmp to convert MIB files into Python code
COPY mibs.zip .
RUN mibdump --mib-borrower="" --mib-source=mibs.zip CISCO-VLAN-MEMBERSHIP-MIB IF-MIB CISCO-MAC-AUTH-BYPASS-MIB IEEE8021-PAE-MIB

# Copy source files
COPY . .

# Launch the app 
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-b", ":8080", "main:application"]
