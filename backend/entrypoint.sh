#!/bin/sh
set -e

echo "Waiting for database..."
until python -c "
import psycopg2, os, sys
try:
    psycopg2.connect(os.environ['DATABASE_URL'].replace('+psycopg2', ''))
except Exception as e:
    sys.exit(1)
"; do
  sleep 1
done

echo "Running Alembic migrations..."
alembic upgrade head

echo "Starting application: $@"
exec "$@"
