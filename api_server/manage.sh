#!/bin/bash
set -a
source ../.env.local
cat config/CONFIGURATION.template.py | envsubst > config/CONFIGURATION.py
set +a

export FLASK_APP=manage:manager
flask $@

git checkout config/CONFIGURATION.py
