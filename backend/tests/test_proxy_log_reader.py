import importlib.util, json, tempfile, unittest, io, contextlib
from pathlib import Path

spec = importlib.util.spec_from_file_location("rl", Path(__file__).resolve().parents[2] / "tools/read-review-proxy-log.py")
rl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rl)


class ReaderTests(unittest.TestCase):
    def test_summary_hides_prompt_and_keys(self):
        rec = {"path": "/openai/v1/chat/completions", "status": 429, "forward_index": 2,
               "body": {"model": "openai/gpt-oss-120b", "messages": [{"role": "user", "content": "SECRET PROMPT TEXT"}],
                        "tools": [{"function": {"name": "StructuredOutput"}}], "tool_choice": "required"},
               "response_headers": {"x-ratelimit-remaining-tokens": "10", "set-cookie": "x"},
               "tail": "rate limit; Bearer gsk_abcdefghij123456"}
        s = rl.summarize(rec)
        out = json.dumps(s)
        self.assertNotIn("SECRET PROMPT", out)
        self.assertNotIn("abcdefghij", out)
        self.assertEqual(s["tools"], ["StructuredOutput"])
        self.assertEqual(s["ratelimit"], {"x-ratelimit-remaining-tokens": "10"})
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "l.log"
            p.write_text(json.dumps(rec) + "\n")
            (Path(td) / "l.log.tripped").write_text("1")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rl.main(str(p))
            self.assertIn(".tripped exists", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
