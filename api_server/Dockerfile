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
FROM python:3.12 AS wheel
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
COPY mibs.zip .
RUN mibdump.py --mib-borrower="" --mib-source=mibs.zip CISCO-VLAN-MEMBERSHIP-MIB IF-MIB CISCO-MAC-AUTH-BYPASS-MIB IEEE8021-PAE-MIB

# Copy source files
COPY . .

# Launch the app 
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-b", ":8080", "main:application"]
