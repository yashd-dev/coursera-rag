"""Runs Laya in its own short-lived process: python -m app.claim_worker jobs.json results.json
Reads [{key, claim, passages}], writes {key: assessment} after every claim. A separate process keeps the model's memory
out of the web server and is simply restarted for the next batch."""
import json
import os
import sys

os.environ.setdefault("PAPERFORGE_CLAIM_CHECKER", "laya")
from app import claim_checker as cc  # noqa: E402

jobs = json.load(open(sys.argv[1]))
out = {}
for j in jobs:
    res = cc.assess(j["claim"], j["passages"])
    out[j["key"]] = res
    json.dump(out, open(sys.argv[2], "w"))
    if res and "error" in res:
        break
