"""Shared PostgreSQL-backed Voyage queue and content cache. No hosted token-count calls."""

import hashlib, json, math, time
from functools import lru_cache
from . import config, db

WINDOW = 61.0
RPM = 3
TPM = 8000  # Account screenshot:10K. Leave20% safety headroom.
SPACING = 22.0


@lru_cache(maxsize=4)
def tokenizer(model):
    from tokenizers import Tokenizer

    # Model-specific official tokenizer. Failure blocks calls, never a character heuristic.
    return Tokenizer.from_pretrained("voyageai/" + model)


def estimate(text, kind):
    return math.ceil(len(tokenizer(config.EMBED_MODEL).encode(text).ids) * 1.1) + 64


def batches(texts, kind):
    batch = []
    total = 0
    for text in texts:
        n = estimate(text, kind)
        if n > TPM:
            raise ValueError(
                "Single input exceeds conservative Voyage TPM batch cap; split input first."
            )
        if batch and (total + n > TPM or len(batch) >= 64):
            yield batch, total
            batch = []
            total = 0
        batch.append(text)
        total += n
    if batch:
        yield batch, total


def delay(records, now, n):
    live = [r for r in records if now - r[0] < WINDOW]
    waits = []
    if live:
        waits.append(max(0, live[-1][0] + SPACING - now))
    if len(live) >= RPM:
        waits.append(live[-RPM][0] + WINDOW - now)
    if sum(r[1] for r in live) + n > TPM and live:
        total = sum(r[1] for r in live) + n
        for at, tokens in live:
            total -= tokens
            if total <= TPM:
                waits.append(at + WINDOW - now)
                break
    return live, max([0] + waits)


def account_key():
    return hashlib.sha256(config.VOYAGE_API_KEY.encode()).hexdigest()[:24]


def reserve(n):
    if n > TPM:
        raise ValueError("Voyage batch too large")
    key = "voyage_rate:organization:shared"
    while True:
        with db.conn().transaction():
            # One organization queue serializes all keys/processes/jobs/queries in this database.
            db.conn().execute(
                "SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (key,)
            )
            now = float(
                db.conn()
                .execute("SELECT extract(epoch FROM clock_timestamp()) AS t")
                .fetchone()["t"]
            )
            rows = db.q("SELECT value FROM meta WHERE key=%s", (key,))
            records = json.loads(rows[0]["value"]) if rows else []
            live, wait = delay(records, now, n)
            if not wait:
                live.append([now, n])
                db.x(
                    "INSERT INTO meta(key,value) VALUES(%s,%s) ON CONFLICT(key) DO UPDATE SET value=EXCLUDED.value",
                    (key, json.dumps(live)),
                )
                return
        time.sleep(wait + 0.1)


def cache_key(text, kind):
    raw = json.dumps(
        [account_key(), config.EMBED_MODEL, config.EMBED_DIM, kind, text],
        ensure_ascii=False,
    )
    return "voyage_cache:" + hashlib.sha256(raw.encode()).hexdigest()


def cached(text, kind):
    rows = db.q("SELECT value FROM meta WHERE key=%s", (cache_key(text, kind),))
    return json.loads(rows[0]["value"]) if rows else None


def store(text, kind, v):
    db.x(
        "INSERT INTO meta(key,value) VALUES(%s,%s) ON CONFLICT(key) DO NOTHING",
        (cache_key(text, kind), json.dumps(v)),
    )


def cached_many(texts, kind):
    keys = [cache_key(t, kind) for t in texts]
    if not keys:
        return []
    rows = db.q("SELECT key,value FROM meta WHERE key = ANY(%s)", (keys,))
    values = {r["key"]: json.loads(r["value"]) for r in rows}
    return [values.get(k) for k in keys]
