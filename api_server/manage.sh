#!/bin/sh
export FLASK_APP=manage:manager
flask "$@"
