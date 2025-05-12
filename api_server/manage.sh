#!/bin/sh
# used to exec "flask" commands INSIDE the container

docker compose exec api_server sh -c 'FLASK_APP=manage:manager flask "$@"' _ "$@"
