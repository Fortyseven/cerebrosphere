#!/bin/bash
export FLASK_APP=server
# get migration message from command line, if not provided, bail out
if [ -z "$1" ]; then
  echo "Usage: $0 <migration_message>"
  exit 1
fi

uv run flask db migrate -m "$1"
uv run flask db upgrade