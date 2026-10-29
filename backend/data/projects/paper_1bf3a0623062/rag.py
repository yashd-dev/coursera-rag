#!/usr/bin/env python3
"""Evidence search for this paper's chat-scoped pgvector collection.
usage: python3 rag.py "question or claim to verify" [top_k] [source_key]"""
import json, sys, urllib.request
q = sys.argv[1]; k = int(sys.argv[2]) if len(sys.argv) > 2 else 5
body = {"thread_id": "paper_1bf3a0623062", "query": q, "k": k, "source_key": sys.argv[3] if len(sys.argv) > 3 else None}
req = urllib.request.Request("http://127.0.0.1:8000/api/internal/retrieve", json.dumps(body).encode(),
                             {"Content-Type": "application/json", "X-Rag-Token": "b84028b7fceb205608be78a5fecce30d"})
for r in json.load(urllib.request.urlopen(req, timeout=300))["results"]:
    print(f"[{r['key']} p.{r['page']} score={r['score']}] {r['text']}\n")
