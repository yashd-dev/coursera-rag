# Railway deployment (single backend image)

The root `Dockerfile` builds one image with the FastAPI API, the ingestion
endpoints, and the full paper toolchain (pandoc for Word export, pdflatex and
bibtex for the PDF). Railway detects and builds it automatically. You deploy;
nothing here deploys itself.

## Required Railway setup

1. New service from this repo. Railway uses the root `Dockerfile` by default.
2. Attach a volume mounted at `/data`. The image sets `PAPERFORGE_DATA=/data`.
   All persistent state lives under `PAPERFORGE_DATA`: `projects/<id>/` holds
   downloaded papers, extracted text, notes, drafts, review artifacts and
   exports. A rebuild or redeploy keeps the volume, so papers and projects
   survive. (Verified in source: `db.thread_dir` and every project write go
   through `config.DATA_DIR`; only system temp files live elsewhere.)
3. Postgres: use your existing Railway Postgres. Set `DATABASE_URL` to it and
   keep `PAPERFORGE_DB_SCHEMA=paperforge` so tables stay isolated. Run once:
   `CREATE EXTENSION IF NOT EXISTS vector` in that database, and keep
   `PAPERFORGE_DB_INITIALIZE=enabled` for the first start only.
4. Set the env vars from `.env.example` (same contract as local; no secrets in
   the repo). `PORT` is injected by Railway; the app binds `0.0.0.0:$PORT`.
5. Healthcheck: the image carries one against `/api/config`.

## Reviewer proxy

If `PAPERFORGE_REVIEW_BASE_URL` points at `127.0.0.1:19441`, the entrypoint
starts the bounded review proxy inside the container before the API
(forwarding to api.groq.com with the request cap in the command). Leave that
variable empty to skip the proxy and call the reviewer provider directly.

## Honest limits

- Access control: the backend has NO user authentication. It was built for
  single-user localhost. The origin check in `main.py` blocks cross-origin
  browser mutations but is not a security boundary against direct API clients:
  anyone who can reach a public URL can use the app. Do not expose it publicly
  without putting authentication in front (or keep it on private networking).
- In-progress jobs are in-memory: a redeploy or restart kills running work and
  unsaved partial output. Files and finished papers on the volume survive;
  running jobs do not.
- Existing local data is NOT moved: files on your laptop stay on your laptop.
  The volume starts empty unless you copy data into it yourself.
- Hosted frontend: build `web/` with `VITE_API_BASE=https://<this backend's origin>` and set `PAPERFORGE_ALLOWED_ORIGINS=https://<frontend origin>` on this service (exact origin, no wildcard). Without it the browser gets HTTP 403 on changes. This is an origin check, not login: keep the backend URL private/trusted. Tested locally with curl: allowed origin passes the guard and CORS preflight, other origins get 403 and no CORS header.
- Single replica only: run state is process-local.

## Not verified

- The image has NOT been built or run (no Docker daemon, podman or buildah was available). The app was started directly with uvicorn on 0.0.0.0:$PORT instead: `/api/config` (the healthcheck URL) returned 200. Package names (poppler-utils, libreoffice-writer, texlive-*) and the Node copy step are standard Debian bookworm choices but untested. The LibreOffice and TeX Live layers make the image large; check it against your Railway plan's image size limit.
- The pdflatex build of the bundled IEEE template was not run inside this image.

## Frontend

This image is the backend only. The Vite dev proxy (`/api` to 127.0.0.1:8000)
is a dev convenience; for a hosted frontend, deploy `web/` as a static build
and point its API calls at this service's URL.
