"""Read-only summary of the bounded review proxy log. No network, no writes.
Usage: read-review-proxy-log.py LOG [N]   (prints the last N records, default 3)
Shows what the provider actually answered (status, rate-limit headers, response tail) and what was sent
(model, tools, tool_choice, response_format, message sizes). Prompt text and credentials are never printed."""

import json, os, re, sys


def summarize(rec):
    body = rec.get("body") if isinstance(rec.get("body"), dict) else {}
    msgs = body.get("messages") or []
    h = rec.get("response_headers") or {}
    tools = [t.get("function", {}).get("name") for t in body.get("tools", []) if isinstance(t, dict)]
    tail = re.sub(r"(?i)(bearer\s+|gsk_|sk-|nvapi-)[A-Za-z0-9._\-]{6,}", r"\1***", str(rec.get("tail", "")))
    return {
        "path": rec.get("path"),
        "forward_index": rec.get("forward_index"),
        "blocked": rec.get("blocked"),
        "status": rec.get("status"),
        "paced_secs": rec.get("paced_secs"),
        "est_tokens": rec.get("est_tokens"),
        "upstream_secs": rec.get("upstream_secs"),
        "error": rec.get("error") or rec.get("proxy_error"),
        "model": body.get("model"),
        "message_chars": sum(len(str(m.get("content", ""))) for m in msgs if isinstance(m, dict)),
        "tools": tools,
        "tool_choice": body.get("tool_choice"),
        "has_response_format": "response_format" in body,
        "max_tokens": body.get("max_tokens") or body.get("max_completion_tokens"),
        "ratelimit": {k: v for k, v in h.items() if k.lower().startswith("x-ratelimit-") or k.lower() == "retry-after"},
        "response_tail": tail[-700:],
    }


def main(path, n=3):
    lines = [l for l in open(path) if l.strip()][-n:]
    for l in lines:
        print(json.dumps(summarize(json.loads(l)), indent=2))
    for ext in (".count", ".tripped"):
        print(ext, "exists" if os.path.exists(path + ext) else "absent", open(path + ext).read().strip() if os.path.exists(path + ext) else "")


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 3)
