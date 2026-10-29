#!/bin/sh
# PaperForge backend container entrypoint.
set -e

if [ -z "$DATABASE_URL" ]; then
  echo "DATABASE_URL is not set; the backend cannot start without Postgres." >&2
  exit 1
fi

# Optional bounded reviewer proxy, launched inside the same container when the
# reviewer base URL points at it. Keeps free-tier reviewer accounts inside
# their rate limits. Skip by leaving PAPERFORGE_REVIEW_BASE_URL unset/empty.
case "$PAPERFORGE_REVIEW_BASE_URL" in
  *127.0.0.1:19441*|*localhost:19441*)
    echo "starting bounded review proxy on 127.0.0.1:19441"
    python3 /app/tools/bounded-review-proxy.py 19441 /data/review-proxy.log 30 https api.groq.com 443 &
    ;;
esac

cd /app/backend
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
