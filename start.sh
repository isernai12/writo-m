#!/usr/bin/env bash
set -euo pipefail

export PORT="${PORT:-8080}"
export API_INTERNAL_URL="${API_INTERNAL_URL:-http://127.0.0.1:8000}"

cd /app
envsubst '${PORT}' < /app/nginx/nginx.conf.template > /etc/nginx/nginx.conf

python -m app.wait_for_db
alembic -c /app/apps/api/alembic.ini upgrade head
python -c "from app.db import SessionLocal; from app.seed import seed_defaults; db=SessionLocal(); seed_defaults(db); db.close()"

uvicorn app.main:app --host 0.0.0.0 --port 8000 &
node /app/apps/web/.next/standalone/server.js &

nginx -g "daemon off;"
