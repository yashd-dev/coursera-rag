import json, os, threading, time
from pathlib import Path
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal
from . import config, db, rag, opencode, pipeline, latexbuild
from .jobs import Job, RUNNING

JOB_LOCK = threading.Lock()
app = FastAPI(title="PaperForge API")
LOCAL_ORIGINS = {
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
}


def parse_allowed_origins(value):
    """PAPERFORGE_ALLOWED_ORIGINS: comma-separated exact origins (scheme://host[:port]) of a hosted
    frontend. No wildcards, paths or other schemes; anything else stops startup rather than being
    silently ignored. This only widens which browser origins may call the API. It is not
    authentication."""
    import re

    out = set()
    for item in (value or "").split(","):
        item = item.strip()
        if not item:
            continue
        if not re.fullmatch(
            r"https?://[A-Za-z0-9]([A-Za-z0-9.-]*[A-Za-z0-9])?(:\d{1,5})?", item
        ):
            raise ValueError(
                "PAPERFORGE_ALLOWED_ORIGINS entries must be exact origins such as "
                "https://app.example.com (no wildcard, path or trailing slash); got: " + item
            )
        out.add(item)
    return out


ALLOWED_ORIGINS = LOCAL_ORIGINS | parse_allowed_origins(
    os.environ.get("PAPERFORGE_ALLOWED_ORIGINS", "")
)


@app.middleware("http")
async def local_mutation_guard(request: Request, call_next):
    if request.method not in ("GET", "HEAD", "OPTIONS"):
        origin = request.headers.get("origin")
        if origin and origin not in ALLOWED_ORIGINS:
            return JSONResponse(
                {"detail": "This origin is not allowed to make changes."},
                status_code=403,
            )
    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted(ALLOWED_ORIGINS),
    allow_methods=["*"],
    allow_headers=["*"],
)


def serialise(t):
    return {
        "id": t["id"],
        "title": t["title"],
        "status": t["status"],
        "template": t["template"],
        "custom": t["custom"] or {},
        "phase": t["phase"],
        "updated": t["updated"],
    }


@app.get("/api/config")
def get_config():
    ok, ver = opencode.available()
    return {
        "model": config.MODEL,
        "opencode": {"available": ok, "version": ver},
        "embedding": {"model": config.EMBED_MODEL, "dims": config.EMBED_DIM},
        "templates": [
            {"id": k, "label": v["label"]} for k, v in config.TEMPLATES.items()
        ],
        "max_sources": config.MAX_SOURCES,
    }


@app.get("/api/threads")
def threads():
    return {"threads": [serialise(t) for t in db.list_threads()]}


class NewThread(BaseModel):
    template: Literal["ieee", "springer"] = "ieee"


@app.post("/api/threads")
def new_thread(b: NewThread = NewThread()):
    return serialise(db.create_thread(b.template))


class Patch(BaseModel):
    title: str | None = None
    status: str | None = None
    custom: dict | None = None
    template: Literal["ieee", "springer"] | None = None


@app.get("/api/threads/{tid}")
def get_thread(tid: str):
    t = db.get_thread(tid)
    if not t:
        raise HTTPException(404)
    return serialise(t)


@app.patch("/api/threads/{tid}")
def patch(tid: str, b: Patch):
    t = db.get_thread(tid)
    if not t:
        raise HTTPException(404)
    kw = {k: v for k, v in b.model_dump().items() if v is not None}
    if "custom" in kw:
        kw["custom"] = {**(t["custom"] or {}), **kw["custom"]}
    if kw:
        db.update_thread(tid, **kw)
    return serialise(db.get_thread(tid))


@app.delete("/api/threads/{tid}")
def delete(tid: str):
    if not db.get_thread(tid):
        raise HTTPException(404)
    if tid in RUNNING and not RUNNING[tid].done:
        raise HTTPException(409, "Wait until this chat finishes before deleting it.")
    db.delete_thread(tid)
    return {"ok": True}


@app.get("/api/threads/{tid}/messages")
def messages(tid: str):
    if not db.get_thread(tid):
        raise HTTPException(404)
    thread = db.get_thread(tid)
    running = tid in RUNNING and not RUNNING[tid].done
    return {
        "messages": db.list_messages(tid),
        "running": running,
        "phase": thread["phase"],
        "execution_state": (
            "running"
            if running
            else (
                "ready"
                if thread["phase"] == "ready"
                else (
                    "paused"
                    if thread["phase"] not in ("new", "scope_pending")
                    else "idle"
                )
            )
        ),
    }


@app.get("/api/threads/{tid}/sources")
def get_sources(tid: str):
    return {
        "sources": [
            {
                k: s[k]
                for k in (
                    "key",
                    "title",
                    "authors",
                    "year",
                    "venue",
                    "url",
                    "pdf_url",
                    "status",
                    "status_note",
                    "pages",
                    "chunk_count",
                )
            }
            for s in db.sources(tid)
        ],
        "rag": rag.stats(tid),
    }


@app.get("/api/threads/{tid}/files/{name}")
def files(tid: str, name: str):
    if name not in pipeline.FINAL_FILES + pipeline.DRAFT_FILES:
        raise HTTPException(404)
    thread = db.get_thread(tid)
    if not thread:
        raise HTTPException(404)
    if name in pipeline.DRAFT_FILES:
        # Unverified drafts are served only while the paper is not ready, under names that say so.
        if thread["phase"] not in ("review_paused", "export_paused"):
            raise HTTPException(
                409, "Draft outputs exist only while claim review is paused."
            )
    elif thread["phase"] != "ready":
        raise HTTPException(
            409,
            "Final exports are unavailable until build, source review and export checks pass.",
        )
    p = db.thread_dir(tid) / name
    if not p.exists():
        raise HTTPException(404)
    return FileResponse(p, filename=name)


class Chat(BaseModel):
    text: str = Field(min_length=1, max_length=50000)
    template: Literal["ieee", "springer"] = "ieee"


@app.post("/api/threads/{tid}/chat")
def chat(tid: str, b: Chat):
    t = db.get_thread(tid)
    if not t:
        raise HTTPException(404)
    with JOB_LOCK:
        if tid in RUNNING and not RUNNING[tid].done:
            raise HTTPException(
                409, "This chat is still working on the previous request."
            )
        db.add_message(tid, "user", [{"type": "text", "text": b.text}])
        template = b.template
        kind, note = pipeline.route(b.text, t)
        job = Job(tid, db.new_id("msg"))
        RUNNING[tid] = job

    def go():
        try:
            if kind == "scope":
                pipeline.run_scope(job, tid, b.text)
            elif kind in ("create", "resume"):
                pipeline.run_create(
                    job, tid, b.text, t["template"] if kind == "resume" else template
                )
            elif kind == "edit":
                pipeline.run_edit(job, tid, b.text)
            else:
                pipeline.run_ask(job, tid, b.text, note)
        except Exception as e:
            import traceback

            traceback.print_exc()
            current = db.get_thread(tid)
            if current and current["phase"] in ("new", "running"):
                db.update_thread(tid, phase="failed_early")
            job.finish(f"{type(e).__name__}: {e}")

    threading.Thread(target=go, daemon=True).start()

    def sse():
        yield "data: " + json.dumps({"t": "route", "route": kind}) + "\n\n"
        for ev in job.stream():
            yield "data: " + json.dumps(ev) + "\n\n"

    return StreamingResponse(
        sse(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


class Retrieve(BaseModel):
    thread_id: str
    query: str
    k: int = Field(default=5, ge=1, le=12)
    source_key: str | None = None


@app.post("/api/internal/retrieve")
def retrieve(b: Retrieve, x_rag_token: str = Header("")):
    """Used by OpenCode runs (rag.py) and the Q&A route. Always scoped to one chat."""
    if x_rag_token != latexbuild.RAG_TOKEN:
        raise HTTPException(403)
    return {"results": rag.retrieve(b.thread_id, b.query, min(b.k, 12), b.source_key)}


@app.post("/api/threads/{tid}/retrieve")
def retrieve_public(tid: str, b: Retrieve):
    """Inspect retrieval directly (used for the demo and tests)."""
    return {
        "results": rag.retrieve(tid, b.query, min(b.k, 12), b.source_key),
        "collection": rag.stats(tid),
    }
