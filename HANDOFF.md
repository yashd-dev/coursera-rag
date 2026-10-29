# PaperForge candidate handoff (2026-10-29)

Full runnable source: backend API (FastAPI), web UI (Vite/React), docker-compose for Postgres+pgvector.
This snapshot adds the candidate reviewer split: drafting and answer generation stay on the default model
(NVIDIA), while claim review and per-sentence Q&A verification can run on a separate reviewer model
(tested with Groq `openai/gpt-oss-120b`). The change is two files versus the prior backend
(see `candidate-changes.diff`): `backend/app/structured.py`, `backend/app/answering.py`.

## STATUS AT HANDOFF: read first
- NOT READY / REVIEW-PAUSED: the test paper did NOT pass claim review. Of 5 spans, 1 was verified
  supported, 3 were left unresolved because the reviewer's evidence excerpts were not verbatim copies of
  the source page (the app accepts nothing and rewrites nothing in that case), and 1 review was interrupted.
  The app deliberately does not auto-retry unresolved spans; the document stays review-paused.
- The sample paper is a SMALL 2-section test artifact from 2 seeded source PDFs plus 1 URL edit. It is not
  a full paper, and the discovery stage (OpenAlex/arXiv search) was NOT exercised in this run.
- The exported Word file passed mechanical checks (7 of 7 headings present, 0 unresolved citation markers).
  That means the conversion is clean. It does NOT mean all claims are verified; see the review status above.
- Q&A was exercised in two tested turns: verified sentences were shown with page citations, and unverifiable
  sentences were withheld. One NVIDIA answer-generation call failed transiently and succeeded on a single
  retry. Q&A behavior beyond these two turns is not established.

## Setup and run
Requirements: Python 3.10+, Node 20+, pandoc >= 2.11 (Word export), TeX with pdflatex/bibtex (paper builds),
Postgres + pgvector (docker compose below, or an embedded local pgserver; pgvector 0.6.2 verified).

Install the document worker CLI at the tested version:
  npm i -g opencode-ai@1.19.5

1. Database: `docker compose up -d db` (or start your pgserver instance).
2. Reviewer proxy (recommended for free-tier reviewer accounts). Start this BEFORE the backend so every
   review call is capped and stopped on the first upstream error:
     python3 tools/bounded-review-proxy.py 19441 proxy.log 30 https api.groq.com 443
   (Args: local port, log file, max requests, upstream scheme/host/port. Serial forwarding, hard request cap,
   circuit breaker on any upstream 4xx/5xx, token-window pacing from the API's own rate-limit headers.
   Auth headers are never logged.)
3. Backend environment and start (from `backend/`):

     export DATABASE_URL='postgresql://postgres:postgres@127.0.0.1:5432/postgres'
     export PAPERFORGE_DB_SCHEMA=paperforge_local
     export PAPERFORGE_DB_INITIALIZE=enabled      # first run only, creates the schema
     export PAPERFORGE_HOSTED_CALLS=enabled
     export PAPERFORGE_ANSWER_CALLS=enabled
     export PAPERFORGE_REVIEW_MODEL=groq/openai/gpt-oss-120b
     export PAPERFORGE_REVIEW_BASE_URL=http://127.0.0.1:19441/openai/v1
     export NVIDIA_API_KEY='...'
     export VOYAGE_API_KEY='...'
     export GROQ_API_KEY='...'
     export FIRECRAWL_API_KEY='...'
     # optional: OPENAI... not needed; OPENALEX_API_KEY and UNSTRUCTURED_API_KEY are optional
     uvicorn app.main:app --host 127.0.0.1 --port 8000

4. Web UI (separate shell): `cd web && npm ci && npm run dev`, then open http://127.0.0.1:5173
   The dev server proxies /api to the backend on 127.0.0.1:8000 (see web/vite.config.ts), so the backend
   must run on port 8000. Production build verified with `npm run build`.

## What was verified in the test run (isolated local database)
- PDF ingestion -> pgvector embeddings -> reading notes -> draft -> LaTeX build: PASS (1-page IEEE PDF).
- Word export plus independent reconversion check: PASS mechanically (caveat above).
- Source Q&A in two tested turns: per-sentence reviewer verification against cited pages; conditional claims
  kept with their conditions; one unverifiable sentence withheld.
- Targeted edit with a new URL: the new paper was downloaded, indexed, and read; only the named section
  changed (byte-level preservation of the rest of the document verified by snapshot diff).
- Sample outputs: `supplements/paper.pdf`, `supplements/paper.docx`, `supplements/paper-source.zip`.
  The comparison table lists only the two original sources; the URL-added source appears as prose plus reference.
- Source-grounding of the added TriForce sentences: "hierarchical speculative decoding", "retrieval-based
  drafting", "StreamingLLM cache", "attention sparsity", and "contextual locality" are explicitly in the
  source. The phrase "two-phase approach" is NOT verbatim-supported by the source (the paper describes a
  hierarchical, multi-level design); treat that wording as unverified.
