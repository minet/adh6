#!/bin/bash
set -a
source ../.env.local
cat config/.env.template | envsubst > config/.env
set +a

export FLASK_APP=manage:manager
flask $@
