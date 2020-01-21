#!/bin/bash
set -a
source ../.env
cat config/CONFIGURATION.template.py | envsubst > config/MANAGE_CONFIGURATION.py
set +a

python manage.py $@
