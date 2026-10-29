import sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pgserver, psycopg
from app import db, config

server = pgserver.get_server(tempfile.mkdtemp(prefix="pf-schema-"), cleanup_mode=None)
config.DATABASE_URL = server.get_uri()
config.DB_INITIALIZE = True
with psycopg.connect(config.DATABASE_URL, autocommit=True) as c:
    c.execute("CREATE EXTENSION vector")
    c.execute("CREATE TABLE public.projects(marker text)")
    c.execute("INSERT INTO public.projects VALUES('keep')")
    c.execute("CREATE TABLE public.threads(marker text)")
    c.execute("INSERT INTO public.threads VALUES('keep-thread')")
t = db.create_thread()
assert db.get_thread(t["id"])["id"] == t["id"]
with psycopg.connect(config.DATABASE_URL) as c:
    assert c.execute("SELECT marker FROM public.projects").fetchall() == [("keep",)]
    assert c.execute("SELECT marker FROM public.threads").fetchall() == [
        ("keep-thread",)
    ]
    assert c.execute("SELECT count(*) FROM paperforge.threads").fetchone()[0] == 1
print("LOCAL_SCHEMA_ISOLATION_PASSED public.projects AND public.threads unchanged")
server.cleanup()
