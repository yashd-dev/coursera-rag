"""Bounded reviewer transport: serial forwarding, hard cap, circuit breaker (terminal on any upstream >=400), TPM pacing from observed x-ratelimit headers. Logs status + response headers + tail. Auth never logged.
Usage: proxy6.py PORT LOG CAP SCHEME HOST UPSTREAM_PORT"""

import json, sys, time, os, re, http.client, threading

PORT = int(sys.argv[1])
LOG = sys.argv[2]
CAP = int(sys.argv[3])
SCHEME = sys.argv[4]
HOST = sys.argv[5]
UPORT = int(sys.argv[6])
COUNT = LOG + ".count"
TRIPPED = LOG + ".tripped"
lock = threading.Lock()
forward_lock = threading.Lock()
COMPLETION_ALLOWANCE = 1500
MAX_PACE_SLEEP = 75.0


def parse_reset(s):
    if not s:
        return 0.0
    m = re.match(r"(?:(\d+)m)?([\d.]+)s", s)
    if not m:
        return 0.0
    return (int(m.group(1) or 0) * 60) + float(m.group(2))


def bump():
    with lock:
        if os.path.exists(TRIPPED):
            return "tripped"
        n = int(open(COUNT).read()) if os.path.exists(COUNT) else 0
        if n >= CAP:
            return None
        open(COUNT, "w").write(str(n + 1))
        return n + 1


def trip():
    with lock:
        open(TRIPPED, "w").write("1")


def pace(body):
    """Wait until the observed token window can fit this request. Grounded only in our own log of real response headers."""
    est = (
        sum(
            len(m.get("content", "") or "")
            for m in body.get("messages", [])
            if isinstance(m, dict)
        )
        // 4
        + COMPLETION_ALLOWANCE
    )
    if not os.path.exists(LOG):
        return 0.0, est
    good = [
        json.loads(l)
        for l in open(LOG)
        if '"status": 200' in l or json.loads(l).get("status") == 200
    ]
    if not good:
        return 0.0, est
    last = good[-1]
    h = last.get("response_headers", {})
    try:
        rem = int(h.get("x-ratelimit-remaining-tokens", "999999"))
    except ValueError:
        return 0.0, est
    if rem >= est:
        return 0.0, est
    reset = parse_reset(h.get("x-ratelimit-reset-tokens"))
    done = last.get("ts", time.time()) + last.get("upstream_secs", 0)
    wait = min(MAX_PACE_SLEEP, max(0.0, reset + 2.0 - (time.time() - done)))
    if wait > 0:
        time.sleep(wait)
    return wait, est


from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(n)
        try:
            body = json.loads(raw)
        except Exception:
            body = {"_unparsed": True}
        with forward_lock:
            # Check the cap and breaker first: a blocked request must return at once, not after a pacing sleep.
            k = bump()
            paced, est = (
                pace(body) if k not in (None, "tripped") and isinstance(body, dict) else (0.0, 0)
            )
            rec = {
                "path": self.path,
                "forward_index": k,
                "ts": time.time(),
                "est_tokens": est,
                "paced_secs": round(paced, 1),
                "body": body,
            }
            if k is None or k == "tripped":
                rec["blocked"] = (
                    "circuit breaker tripped"
                    if k == "tripped"
                    else "request cap reached"
                )
                open(LOG, "a").write(json.dumps(rec) + "\n")
                # 403, not 429: OpenCode retries 429 up to 5 times. This is a deliberate local stop with no
                # provider call, so it must be terminal for the client.
                self.send_response(403)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(
                    json.dumps(
                        {"error": "bounded review proxy stopped this request locally: " + rec["blocked"] + "; no provider call was made"}
                    ).encode()
                )
                return
            t0 = time.time()
            try:
                conn = (
                    http.client.HTTPSConnection
                    if SCHEME == "https"
                    else http.client.HTTPConnection
                )
                c = conn(HOST, UPORT, timeout=110)
                c.request(
                    "POST",
                    self.path,
                    raw,
                    {
                        "Content-Type": "application/json",
                        "Authorization": self.headers.get("Authorization", ""),
                        "Accept": self.headers.get("Accept", "*/*"),
                    },
                )
                r = c.getresponse()
                rec["status"] = r.status
                rec["response_headers"] = {k2: v2 for k2, v2 in r.getheaders()}
                if r.status >= 400:
                    trip()
                self.send_response(r.status)
                self.send_header(
                    "Content-Type", r.getheader("Content-Type", "text/event-stream")
                )
                for hn, hv in r.getheaders():
                    if (
                        hn.lower().startswith("x-ratelimit-")
                        or hn.lower() == "retry-after"
                    ):
                        self.send_header(hn, hv)
                self.end_headers()
                tail = b""
                try:
                    while True:
                        ch = r.read1(65536)
                        if not ch:
                            break
                        tail = (tail + ch)[-6000:]
                        self.wfile.write(ch)
                        self.wfile.flush()
                    rec["upstream_secs"] = round(time.time() - t0, 1)
                except Exception as e:
                    rec["error"] = type(e).__name__ + ": " + str(e)[:120]
                    rec["upstream_secs"] = round(time.time() - t0, 1)
                rec["tail"] = tail.decode("utf8", "ignore")[-1500:]
            except Exception as e:
                rec["proxy_error"] = type(e).__name__ + ": " + str(e)[:200]
                try:
                    self.send_response(502)
                    self.end_headers()
                except Exception:
                    pass
            open(LOG, "a").write(json.dumps(rec) + "\n")


ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
