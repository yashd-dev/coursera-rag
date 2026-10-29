# Save as review-proxy-diagnose.py (replace the old one), then run from your repo folder:
#   python3 review-proxy-diagnose.py probe-1.log
# Read-only. With no argument it looks for probe-1.log, proxy.log, review-proxy.log in the current folder,
# backend/ and /data. Prints no prompt text or secrets: only time, status, error, model, pacing, token estimate,
# rate-limit headers, count/tripped state and (failures only) the first 300 characters of the provider response.
import json, os, re, sys, time

def proxies():  # running proxy processes: command line + start folder only (never environment)
    out = []
    if os.path.isdir("/proc"):
        for pid in filter(str.isdigit, os.listdir("/proc")):
            try:
                cmd = open(f"/proc/{pid}/cmdline", "rb").read().replace(b"\0", b" ").decode(errors="replace")
                if "bounded-review-proxy.py" in cmd and "review-proxy-diagnose" not in cmd and "python" in cmd:
                    out.append((pid, cmd.strip(), os.readlink(f"/proc/{pid}/cwd")))
            except OSError:
                pass
    return out

for pid, cmd, cwd in proxies():
    print(f"RUNNING proxy pid={pid} cwd={cwd}\n  cmd={cmd}")
if not proxies():
    print("No bounded-review-proxy process is running right now.")

args = sys.argv[1:]
cands = args or ["probe-1.log", "proxy.log", "review-proxy.log", "backend/proxy.log", "/data/review-proxy.log"]
found = [os.path.abspath(p) for p in cands if os.path.exists(p)]
for pid, cmd, cwd in proxies():  # also resolve the running proxy's own log argument
    parts = cmd.split()
    try:
        lp = parts[parts.index("19441") + 1] if "19441" in parts else None
        if lp:
            q = lp if os.path.isabs(lp) else os.path.join(cwd, lp)
            if os.path.exists(q) and q not in found:
                found.append(q)
    except ValueError:
        pass
if not found:
    print("Log file not found:", ", ".join(cands), "(checked from", os.getcwd() + "). No request has been logged there yet, or it is in another folder.")
for p in found:
    print("== LOG", p, "| .count:", open(p + ".count").read().strip() if os.path.exists(p + ".count") else "absent",
          "| .tripped:", "EXISTS (safety stop active)" if os.path.exists(p + ".tripped") else "absent")
    for l in [x for x in open(p) if x.strip()][-3:]:
        r = json.loads(l); h = r.get("response_headers") or {}; b = r.get("body") if isinstance(r.get("body"), dict) else {}
        bad = (r.get("status") or 0) >= 400 or r.get("error") or r.get("proxy_error") or r.get("blocked")
        tail = re.sub(r"(?i)(bearer\s+|gsk_|sk-|nvapi-)[A-Za-z0-9._\-]{6,}", r"\1***", str(r.get("tail", "")))[:300] if bad else ""
        print(json.dumps({"time": time.strftime("%H:%M:%S", time.localtime(r.get("ts", 0))), "status": r.get("status"),
              "blocked": r.get("blocked"), "error": r.get("error") or r.get("proxy_error"), "model": b.get("model"),
              "tool_choice": b.get("tool_choice"), "has_response_format": "response_format" in b,
              "paced_secs": r.get("paced_secs"), "est_tokens": r.get("est_tokens"), "upstream_secs": r.get("upstream_secs"),
              "ratelimit": {k: v for k, v in h.items() if k.lower().startswith("x-ratelimit-") or k.lower() == "retry-after"},
              "failure_response_head": tail}))
