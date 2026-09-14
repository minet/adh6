FROM python:3.12-alpine

RUN pip install --no-cache-dir snmpsim==1.2.2 pysmi==2.0.0 pysnmp==7.1.29 \
    && adduser -S -D -H snmpsim

EXPOSE 161/udp

CMD ["snmpsim-command-responder", "--data-dir=/snmpsim/data", "--agent-udpv4-endpoint=0.0.0.0:161", "--process-user=snmpsim", "--process-group=nogroup"]
