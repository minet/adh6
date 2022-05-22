#!/bin/sh
set -a
source ../.env.local
set +a

export FLASK_APP=manage:manager
flask "$@"
