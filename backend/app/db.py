"""PostgreSQL + pgvector persistence. Every chunk embedding lives in Postgres (`chunks.embedding vector(1024)` by default)."""

import json, threading, time, uuid, shutil, re
from psycopg import sql
import psycopg
from psycopg.rows import dict_row
from . import config

_local = threading.local()
_initialised = False
_init_lock = threading.Lock()

SCHEMA = f"""

CREATE TABLE IF NOT EXISTS threads(
  id TEXT PRIMARY KEY, title TEXT, status TEXT DEFAULT 'regular', template TEXT DEFAULT 'ieee',
  custom JSONB DEFAULT '{{}}', phase TEXT DEFAULT 'new', created DOUBLE PRECISION, updated DOUBLE PRECISION);
CREATE TABLE IF NOT EXISTS messages(
  id TEXT PRIMARY KEY, thread_id TEXT REFERENCES threads(id) ON DELETE CASCADE, role TEXT, content JSONB,
  created DOUBLE PRECISION, seq BIGSERIAL);
CREATE TABLE IF NOT EXISTS sources(
  id TEXT PRIMARY KEY, thread_id TEXT REFERENCES threads(id) ON DELETE CASCADE, key TEXT, title TEXT, authors TEXT,
  year INTEGER, venue TEXT, doi TEXT, url TEXT, pdf_url TEXT, abstract TEXT, cited_by INTEGER, origin TEXT,
  status TEXT, status_note TEXT, pdf_path TEXT, text_path TEXT, notes_path TEXT, pages INTEGER, chunk_count INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS chunks(
  id BIGSERIAL PRIMARY KEY, thread_id TEXT REFERENCES threads(id) ON DELETE CASCADE,
  source_id TEXT REFERENCES sources(id) ON DELETE CASCADE, page INTEGER, chunk_index INTEGER,
  text TEXT, embedding vector({config.EMBED_DIM}));
CREATE INDEX IF NOT EXISTS chunks_thread_idx ON chunks(thread_id);
CREATE INDEX IF NOT EXISTS chunks_embedding_hnsw ON chunks USING hnsw (embedding vector_cosine_ops);
"""

TABLES = ("threads", "messages", "sources", "chunks", "meta")


def _namespace():
    name = config.DB_SCHEMA
    if (
        not re.fullmatch(r"[a-z][a-z0-9_]{0,62}", name)
        or name in ("public", "information_schema")
        or name.startswith("pg_")
    ):
        raise RuntimeError(
            "PAPERFORGE_DB_SCHEMA must be a dedicated lowercase schema, not public/system."
        )
    return name


def qualified(statement):
    # Only known SQL table positions, never content or parameters. No public fallback.
    schema = _namespace()
    names = "|".join(TABLES)
    pattern = (
        r"(?i)(\b(?:FROM|JOIN|INTO|UPDATE|REFERENCES|TABLE IF NOT EXISTS|ON)\s+)("
        + names
        + r")\b"
    )
    return re.sub(
        pattern, lambda m: m[1] + '"' + schema + '"."' + m[2].lower() + '"', statement
    )


def conn():
    global _initialised
    if not config.DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set.")
    schema = _namespace()
    c = getattr(_local, "c", None)
    if (
        c is not None
        and not c.closed
        and c.info.transaction_status == psycopg.pq.TransactionStatus.IDLE
    ):
        try:
            c.execute("SELECT 1")
        except (psycopg.OperationalError, psycopg.InterfaceError):
            c.close()
            c = None
            _local.c = None
    if c is None or c.closed:
        c = psycopg.connect(
            config.DATABASE_URL,
            autocommit=True,
            row_factory=dict_row,
            connect_timeout=15,
            options="-c statement_timeout=30000",
            keepalives=1,
            keepalives_idle=15,
            keepalives_interval=5,
            keepalives_count=3,
            tcp_user_timeout=30000,
        )
        _local.c = c
        c.execute(
            sql.SQL("SET search_path TO {}, pg_catalog, public").format(
                sql.Identifier(schema)
            )
        )
    if not _initialised:
        with _init_lock:
            if not _initialised:
                exists = c.execute(
                    "SELECT to_regclass(%s) AS name", (schema + ".threads",)
                ).fetchone()["name"]
                if not exists and not config.DB_INITIALIZE:
                    raise RuntimeError(
                        "PaperForge schema is not initialized. Explicit authorization and PAPERFORGE_DB_INITIALIZE=enabled are required."
                    )
                vector = c.execute(
                    "SELECT extversion FROM pg_extension WHERE extname='vector'"
                ).fetchone()
                if not vector:
                    raise RuntimeError(
                        "pgvector is not enabled. Ask the database owner to enable it; the app will not install extensions automatically."
                    )
                if config.DB_INITIALIZE:
                    with c.transaction():
                        c.execute(
                            sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(
                                sql.Identifier(schema)
                            )
                        )
                        c.execute(qualified(SCHEMA))
                _initialised = True
    return c


def q(statement, args=()):
    # Read-only callers may safely retry a stale idle connection once.
    # Never replay a mutation or an in-transaction SELECT after a disconnect.
    for attempt in range(2):
        c = conn()
        in_transaction = c.info.transaction_status != psycopg.pq.TransactionStatus.IDLE
        try:
            with c.cursor() as cur:
                cur.execute(qualified(statement), args)
                return cur.fetchall() if cur.description else []
        except (psycopg.OperationalError, psycopg.InterfaceError):
            c.close()
            _local.c = None
            if (
                attempt
                or in_transaction
                or not statement.lstrip().upper().startswith("SELECT")
            ):
                raise


def x(statement, args=()):
    conn().execute(qualified(statement), args)


def new_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def validate_thread_id(tid):
    if not re.fullmatch(r"paper_[a-f0-9]{12}", tid):
        raise ValueError("Invalid paper ID")
    return tid


def thread_dir(tid):
    validate_thread_id(tid)
    p = config.DATA_DIR / "projects" / tid
    p.mkdir(parents=True, exist_ok=True)
    return p


def create_thread(template="ieee"):
    tid = new_id("paper")
    now = time.time()
    x(
        "INSERT INTO threads(id,title,template,created,updated) VALUES(%s,%s,%s,%s,%s)",
        (tid, None, template, now, now),
    )
    thread_dir(tid)
    return get_thread(tid)


def get_thread(tid):
    r = q("SELECT * FROM threads WHERE id=%s", (tid,))
    return r[0] if r else None


def list_threads():
    return q("SELECT * FROM threads ORDER BY updated DESC")


def update_thread(tid, **kw):
    if "custom" in kw:
        kw["custom"] = json.dumps(kw["custom"])
    kw["updated"] = time.time()
    cols = ",".join(f"{k}=%s" for k in kw)
    x(f"UPDATE threads SET {cols} WHERE id=%s", (*kw.values(), tid))


def delete_thread(tid):
    validate_thread_id(tid)
    x("DELETE FROM threads WHERE id=%s", (tid,))
    shutil.rmtree(config.DATA_DIR / "projects" / tid, ignore_errors=True)


def add_message(tid, role, content, mid=None):
    mid = mid or new_id("msg")
    x(
        """INSERT INTO messages(id,thread_id,role,content,created) VALUES(%s,%s,%s,%s,%s)
         ON CONFLICT(id) DO UPDATE SET content=EXCLUDED.content""",
        (mid, tid, role, json.dumps(content), time.time()),
    )
    x("UPDATE threads SET updated=%s WHERE id=%s", (time.time(), tid))
    return mid


def list_messages(tid):
    return q(
        "SELECT id,role,content,created FROM messages WHERE thread_id=%s ORDER BY seq",
        (tid,),
    )


def add_source(tid, s):
    sid = new_id("src")
    cols = ["id", "thread_id"] + list(s)
    x(
        f"INSERT INTO sources({','.join(cols)}) VALUES({','.join(['%s']*len(cols))})",
        (sid, tid, *s.values()),
    )
    return sid


def sources(tid):
    return q(
        "SELECT * FROM sources WHERE thread_id=%s ORDER BY year DESC NULLS LAST, title",
        (tid,),
    )


def sources_by_key(tid):
    return {s["key"]: s for s in q("SELECT * FROM sources WHERE thread_id=%s", (tid,))}


def update_source(sid, **kw):
    cols = ",".join(f"{k}=%s" for k in kw)
    x(f"UPDATE sources SET {cols} WHERE id=%s", (*kw.values(), sid))


def meta_add(key, n):
    """Atomically add n to a counter in `meta` and return the new total."""
    return int(
        q(
            """INSERT INTO meta(key,value) VALUES(%s,%s) ON CONFLICT(key) DO UPDATE SET value=(meta.value::bigint+%s)::text
                    RETURNING value""",
            (key, str(n), n),
        )[0]["value"]
    )


def meta_get(key):
    r = q("SELECT value FROM meta WHERE key=%s", (key,))
    return int(r[0]["value"]) if r else 0
