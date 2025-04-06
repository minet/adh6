#!/bin/sh
set -a
. ../.env.local
set +a

export FLASK_APP=manage:manager
flask "$@"
