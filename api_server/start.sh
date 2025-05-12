#!/bin/sh

# upgrade database to head
FLASK_APP=manage:manager flask db upgrade head

# start the application
uvicorn --port 8080 --host 0.0.0.0 main:application
