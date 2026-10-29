import json, os, socket, subprocess, sys, tempfile, time, unittest
from pathlib import Path
from unittest.mock import patch
import http.client
from app import structured

PROXY = str(Path(__file__).resolve().parents[2] / "tools/bounded-review-proxy.py")


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class ProxyTests(unittest.TestCase):
    def start(self, td, cap):
        port = free_port()
        p = subprocess.Popen([sys.executable, PROXY, str(port), str(Path(td) / "p.log"), str(cap), "http", "127.0.0.1", "9"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(50):
            try:
                socket.create_connection(("127.0.0.1", port), timeout=0.2).close()
                break
            except OSError:
                time.sleep(0.1)
        self.addCleanup(p.kill)
        return port

    def post(self, port):
        c = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
        c.request("POST", "/openai/v1/chat/completions", json.dumps({"messages": [{"content": "x" * 40000}]}), {"Content-Type": "application/json"})
        r = c.getresponse()
        return r.status, r.read().decode()

    def test_cap_stop_is_instant_terminal_and_makes_no_upstream_call(self):
        with tempfile.TemporaryDirectory() as td:
            port = self.start(td, 0)
            t = time.time()
            status, body = self.post(port)
            self.assertLess(time.time() - t, 3)
            self.assertEqual(status, 403)
            self.assertIn("request cap reached", body)
            self.assertIn("no provider call", body)
            rec = json.loads((Path(td) / "p.log").read_text().splitlines()[-1])
            self.assertEqual(rec["blocked"], "request cap reached")
            self.assertEqual(rec["paced_secs"], 0.0)
            self.assertNotIn("status", rec)

    def test_tripped_breaker_is_also_terminal(self):
        with tempfile.TemporaryDirectory() as td:
            port = self.start(td, 5)
            (Path(td) / "p.log.tripped").write_text("1")
            status, body = self.post(port)
            self.assertEqual(status, 403)
            self.assertIn("circuit breaker tripped", body)


class PreflightTests(unittest.TestCase):
    def test_closed_loopback_port_gives_start_instruction(self):
        msg = structured.proxy_unreachable(f"http://127.0.0.1:{free_port()}/openai/v1")
        self.assertIn("nothing is listening", msg)
        self.assertIn("bounded-review-proxy.py", msg)

    def test_listening_remote_and_empty_urls_pass(self):
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            s.listen(1)
            self.assertEqual(structured.proxy_unreachable(f"http://127.0.0.1:{s.getsockname()[1]}/v1"), "")
        self.assertEqual(structured.proxy_unreachable("https://api.groq.com/openai/v1"), "")
        self.assertEqual(structured.proxy_unreachable(""), "")

    def test_run_stops_before_any_server_or_call_when_proxy_down(self):
        with tempfile.TemporaryDirectory() as td:
            cwd = Path(td)
            (cwd / "opencode.json").write_text(json.dumps({"agent": {"paperforge": {}}}))
            base = f"http://127.0.0.1:{free_port()}/openai/v1"
            with patch.dict(os.environ, {"PAPERFORGE_REVIEW_BASE_URL": base}), patch.object(structured.subprocess, "Popen", side_effect=AssertionError("must not start a server")):
                text, ok, _, events = structured.run(cwd, "p", {"type": "object"}, model_id="groq/openai/gpt-oss-120b")
            self.assertFalse(ok)
            self.assertEqual(structured.outcome_code(events), "proxy_unreachable")
            self.assertIn("nothing is listening", events[0]["detail"])


if __name__ == "__main__":
    unittest.main()
