#!/bin/bash
set -a
source ../.env
cat config/CONFIGURATION.template.py | envsubst > config/CONFIGURATION.py
set +a

python3.7 manage.py $@
git checkout config/CONFIGURATION.py
