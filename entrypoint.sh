#!/bin/sh

set -e

echo "Waiting for database..."

# Wait until Postgres accepts TCP connections (portable; no pg_isready required).
python - <<'PY'
import os
import socket
import sys
import time

host = os.environ.get("DB_HOST", "db")
port = int(os.environ.get("DB_PORT") or "5432")
deadline = time.time() + 60

while time.time() < deadline:
    try:
        with socket.create_connection((host, port), timeout=2):
            sys.exit(0)
    except OSError:
        time.sleep(1)

print(f"Database not ready at {host}:{port}", file=sys.stderr)
sys.exit(1)
PY

python manage.py migrate --noinput

# DatabaseCache table (unmanaged CacheTable model); required for FallbackCache.
python manage.py createcachetable

python manage.py collectstatic --noinput

exec "$@"
