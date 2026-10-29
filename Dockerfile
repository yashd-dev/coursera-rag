# PaperForge backend - single all-in-one image (API + ingestion + LaTeX/PDF/Word toolchain).
# Railway picks this up automatically (docs.railway.com/deploy/dockerfiles).

FROM python:3.11-bookworm AS base

# Node 20 for the opencode CLI (the backend shells out to it for model calls).
COPY --from=node:20-bookworm-slim /usr/local /usr/local

# poppler-utils: pdftotext/pdfinfo/pdftoppm, used by source ingestion and export checks.
# libreoffice-writer: soffice, used to re-convert the Word file as an export check.
# Pandoc (Word export; app requires >= 2.11, bookworm ships 2.17) and a minimal
# TeX Live set: the IEEE/springer classes and .bst files are bundled in
# backend/app/templates/, so only base+recommended packages are required.
RUN apt-get update && apt-get install -y --no-install-recommends \
      pandoc \
      poppler-utils \
      libreoffice-writer \
      texlive-latex-base \
      texlive-latex-recommended \
      texlive-fonts-recommended \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

RUN npm install -g opencode-ai@1.19.5 && opencode --version

COPY backend backend
COPY tools tools

ENV PAPERFORGE_DATA=/data \
    PORT=8000

# /data is the persistent volume mount point: projects, downloaded papers,
# chats and exports all live under PAPERFORGE_DATA (see RAILWAY.md).
VOLUME ["/data"]

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s \
  CMD python -c "import os,urllib.request;urllib.request.urlopen('http://127.0.0.1:'+os.environ.get('PORT','8000')+'/api/config',timeout=4)" || exit 1

ENTRYPOINT ["/app/tools/docker-entrypoint.sh"]
