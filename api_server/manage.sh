#!/bin/bash
set -a
source ../.env.local
cat config/CONFIGURATION.template.py | envsubst > config/CONFIGURATION.py
set +a

python3 manage.py $@
git checkout config/CONFIGURATION.py
