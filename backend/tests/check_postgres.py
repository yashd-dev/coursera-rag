import sys, tempfile, os

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1]))
import pgserver
from unittest.mock import patch
from app import db, rag, config

server = pgserver.get_server(
    tempfile.mkdtemp(prefix="paperforge-pg-test-"), cleanup_mode=None
)
config.DATABASE_URL = server.get_uri()
config.DB_INITIALIZE = True
server.psql("CREATE EXTENSION IF NOT EXISTS vector;")
a = db.create_thread()
b = db.create_thread()
sa = db.add_source(a["id"], {"key": "onlyA", "title": "A", "status": "indexed"})
sb = db.add_source(b["id"], {"key": "onlyB", "title": "B", "status": "indexed"})
v = [1.0] + [0.0] * (config.EMBED_DIM - 1)
for tid, sid, text in (
    (a["id"], sa, "SECRET_A_SYNTHETIC"),
    (b["id"], sb, "SECRET_B_SYNTHETIC"),
):
    db.x(
        "INSERT INTO chunks(thread_id,source_id,page,chunk_index,text,embedding) VALUES(%s,%s,1,0,%s,%s::vector)",
        (tid, sid, text, rag.vec(v)),
    )
with patch.object(rag, "embed", return_value=[v]):
    ah = rag.retrieve(a["id"], "fixture", 6)
    bh = rag.retrieve(b["id"], "fixture", 6)
    assert [r["key"] for r in ah] == ["onlyA"], ah
    assert [r["key"] for r in bh] == ["onlyB"], bh
    assert rag.retrieve("nonexistent", "fixture", 6) == []
print(
    "LIVE_POSTGRES_ISOLATION_OK",
    server.psql("select extversion from pg_extension where extname='vector';"),
)
db.delete_thread(a["id"])
db.delete_thread(b["id"])
server.cleanup()
