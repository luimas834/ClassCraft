#!/bin/sh
# Runs before the container's command.
# Later iterations add the database migrations and the first-start setup here.
set -e

exec "$@"
