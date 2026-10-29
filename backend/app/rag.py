"""Chat-scoped vector RAG: page-aware chunks -> local CPU embeddings -> pgvector -> cosine top-k.
Every query is filtered by thread_id, so one chat can never retrieve another chat's documents.
"""

import re, threading, time, math
from . import config, db

_model = None
_mlock = threading.Lock()
_tokens_used = 0


class EmbeddingError(RuntimeError):
    pass


def _voyage(texts, input_type):
    global _tokens_used
    import httpx
    from . import voyage_guard as guard

    if not config.VOYAGE_API_KEY:
        raise EmbeddingError("VOYAGE_API_KEY is not set.")
    if not config.HOSTED_CALLS:
        raise EmbeddingError("Hosted calls are disabled.")
    out = guard.cached_many(texts, input_type)
    missing = list(dict.fromkeys(t for t, v in zip(texts, out) if v is None))
    for batch, reserved in guard.batches(missing, input_type):
        if _tokens_used + reserved > config.EMBED_TOKEN_BUDGET:
            raise EmbeddingError("Process embedding token budget exhausted.")
        if db.meta_get("voyage_tokens") + reserved > config.VOYAGE_TOKEN_CAP:
            raise EmbeddingError("App-side Voyage free-usage cap reached.")
        for attempt in range(3):
            guard.reserve(reserved)
            r = httpx.post(
                "https://api.voyageai.com/v1/embeddings",
                timeout=40,
                headers={"Authorization": f"Bearer {config.VOYAGE_API_KEY}"},
                json={
                    "input": batch,
                    "model": config.EMBED_MODEL,
                    "input_type": input_type,
                    "output_dimension": config.EMBED_DIM,
                    "truncation": False,
                },
            )
            if r.status_code != 429:
                break
            if attempt == 2:
                raise EmbeddingError(
                    "Voyage rate limited after bounded retries; completed chunks cached, resume later."
                )
            try:
                wait = float(r.headers.get("Retry-After", "61"))
            except ValueError:
                wait = 61
            if wait > 300:
                raise EmbeddingError(
                    "Voyage Retry-After exceeds bounded wait; resume later."
                )
            time.sleep(max(61, wait))
        if r.status_code != 200:
            raise EmbeddingError(
                f"Voyage API returned HTTP {r.status_code}; no local fallback."
            )
        j = r.json()
        n = j.get("usage", {}).get("total_tokens")
        if not isinstance(n, int) or n < 0:
            raise EmbeddingError("Voyage usage missing; pause for reconciliation.")
        _tokens_used += n
        db.meta_add("voyage_tokens", n)
        vectors = [d["embedding"] for d in sorted(j["data"], key=lambda d: d["index"])]
        if len(vectors) != len(batch) or any(
            len(v) != config.EMBED_DIM
            or any(not isinstance(x, (int, float)) or not math.isfinite(x) for x in v)
            for v in vectors
        ):
            raise EmbeddingError("Invalid Voyage vector response.")
        for text, v in zip(batch, vectors):
            guard.store(text, input_type, v)
        if n > reserved:
            raise EmbeddingError(
                "Provider token count exceeded reservation; cached result retained, pause for accounting review."
            )
    return guard.cached_many(texts, input_type)


def _local(texts, input_type):
    global _model
    with _mlock:
        if _model is None:
            from fastembed import TextEmbedding

            _model = TextEmbedding(config.EMBED_MODEL, threads=2)
    pre = (
        "Represent this sentence for searching relevant passages: "
        if input_type == "query" and "bge" in config.EMBED_MODEL
        else ""
    )
    return [v.tolist() for v in _model.embed([pre + t for t in texts], batch_size=8)]


def embed(texts, input_type="document"):
    """input_type is 'document' for chunks and 'query' for questions, consistently for every call."""
    if input_type not in ("document", "query"):
        raise EmbeddingError("Invalid embedding input type.")
    if config.EMBED_PROVIDER not in ("voyage", "local"):
        raise EmbeddingError("Unknown embedding provider; refusing local fallback.")
    result = (_voyage if config.EMBED_PROVIDER == "voyage" else _local)(
        texts, input_type
    )
    if len(result) != len(texts):
        raise EmbeddingError("Embedding response count does not match inputs.")
    if any(
        len(v) != config.EMBED_DIM
        or any(not isinstance(n, (int, float)) or not math.isfinite(n) for n in v)
        for v in result
    ):
        raise EmbeddingError("Invalid embedding dimensions or non-finite values.")
    return result


def tokens_used():
    return _tokens_used


def vec(v):
    return "[" + ",".join(f"{x:.6f}" for x in v) + "]"


def chunk_pages(pages, size=1100, overlap=180):
    """pages: list of (page_number, text). Chunks never cross a page so every chunk has an exact page."""
    out = []
    for pno, text in pages:
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        if len(text) < 80:
            continue
        paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        cur = ""
        for p in paras:
            if len(cur) + len(p) + 1 <= size:
                cur = (cur + "\n" + p).strip()
                continue
            if cur:
                out.append((pno, cur))
            while len(p) > size:
                out.append((pno, p[:size]))
                p = p[size - overlap :]
            cur = p
        if cur:
            out.append((pno, cur))
    return out


def assert_collection_model():
    """Vectors from different models are incompatible: refuse instead of silently mixing."""
    row = db.q("SELECT value FROM meta WHERE key='embedding'")
    want = f"{config.EMBED_PROVIDER}:{config.EMBED_MODEL}:{config.EMBED_DIM}"
    if not row:
        db.x("INSERT INTO meta(key,value) VALUES('embedding',%s)", (want,))
    elif row[0]["value"] != want:
        raise EmbeddingError(
            f"This database was built with {row[0]['value']} but the app is configured for {want}. Re-embed or use a fresh database."
        )


def index_source(thread_id, source_id, pages):
    assert_collection_model()
    chunks = chunk_pages(pages)
    if not chunks:
        return 0
    embs = []
    for i in range(0, len(chunks), 32):
        embs += embed([c[1] for c in chunks[i : i + 32]], "document")
    with db.conn().transaction():
        with db.conn().cursor() as cur:
            cur.execute(
                db.qualified("DELETE FROM chunks WHERE source_id=%s"), (source_id,)
            )
            cur.executemany(
                db.qualified(
                    "INSERT INTO chunks(thread_id,source_id,page,chunk_index,text,embedding) VALUES(%s,%s,%s,%s,%s,%s::vector)"
                ),
                [
                    (thread_id, source_id, p, i, t, vec(e))
                    for i, ((p, t), e) in enumerate(zip(chunks, embs))
                ],
            )
    db.update_source(source_id, chunk_count=len(chunks))
    return len(chunks)


def retrieve(thread_id, query, k=6, source_key=None):
    assert_collection_model()
    qv = vec(embed([query], "query")[0])
    sql = (
        """SELECT c.id, c.page, c.chunk_index, c.text, s.key, s.title, s.year, s.authors,
                    1 - (c.embedding <=> %s::vector) AS score
             FROM chunks c JOIN sources s ON s.id=c.source_id
             WHERE c.thread_id=%s"""
        + (" AND s.key=%s" if source_key else "")
        + " ORDER BY c.embedding <=> %s::vector LIMIT %s"
    )
    args = [qv, thread_id] + ([source_key] if source_key else []) + [qv, k]
    return [dict(r, score=round(float(r["score"]), 4)) for r in db.q(sql, args)]


def stats(thread_id):
    r = db.q(
        "SELECT count(*) n, count(DISTINCT source_id) docs FROM chunks WHERE thread_id=%s",
        (thread_id,),
    )[0]
    return {
        "chunks": r["n"],
        "documents": r["docs"],
        "embedding_model": f"{config.EMBED_PROVIDER}:{config.EMBED_MODEL}",
        "dimensions": config.EMBED_DIM,
        "index": "pgvector HNSW (cosine)",
    }
