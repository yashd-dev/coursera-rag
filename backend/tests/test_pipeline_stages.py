"""run_create is split into stages that both the legacy path and the LangGraph nodes call. These tests drive the
whole chain with stubs: the final phase, and that an unverified draft never becomes ready."""
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from app import pipeline, jobs

try:
    from langgraph.checkpoint.memory import InMemorySaver
    from app.orchestrator import graph, llm
    HAVE_LG = True
except ImportError:
    HAVE_LG = False


class FakeJob:
    def __init__(self):
        self.out, self.done, self.parts, self.tools, self.error = [], False, [], [], None

    def text(self, s):
        self.out.append(s)

    def tool_start(self, n, a):
        self.tools.append(n)
        return n

    def tool_done(self, *a, **k):
        pass

    def finish(self, error=None):
        self.done, self.error = True, error


class Harness:
    def __init__(self, test, index_n=3, review_ok=True, build_ok=True, export_ok=True):
        self.thread = {"phase": "new", "template": "ieee", "custom": {}}
        self.phases = []
        self.calls = []
        root = Path(tempfile.mkdtemp())
        (root / "paper").mkdir()
        (root / "paper" / "main.pdf").write_bytes(b"%PDF")

        def upd(tid, **kw):
            self.thread.update({k: v for k, v in kw.items() if k in ("phase", "template", "custom")})
            if "phase" in kw:
                self.phases.append(kw["phase"])

        def rec(name, ret):
            def f(*a, **k):
                self.calls.append(name)
                return ret(*a) if callable(ret) else ret
            return f

        res = {"ok": build_ok, "pages": 6, "errors": [], "undefined_citations": []}
        v = {"rendered": True} if export_ok else {"rendered": False}
        self.patches = [
            mock.patch("app.latexbuild.prepare", lambda tid, tpl: root),
            mock.patch("app.opencode.available", lambda: (True, "x")),
            mock.patch("app.opencode.write_config", lambda *a, **k: None),
            mock.patch("app.db.get_thread", lambda tid: self.thread),
            mock.patch("app.db.update_thread", upd),
            mock.patch("app.db.sources", lambda tid: [{"status": "indexed", "key": "k"}]),
            mock.patch("app.pipeline.plan", rec("plan", {"title": "T", "sections": [], "request": "r"})),
            mock.patch("app.pipeline.discover_and_index", rec("discover", index_n)),
            mock.patch("app.pipeline.read_papers", rec("read", ["n"])),
            mock.patch("app.latexbuild.write_bib", rec("bib", [{"key": "k"}])),
            mock.patch("app.drafting.generate", rec("draft", (True, "sess"))),
            mock.patch("app.pipeline.build_loop", rec("build", (res, "sess"))),
            mock.patch("app.pipeline.review_claims", rec("review", (review_ok, "sess"))),
            mock.patch("app.pipeline.export_all", rec("export", ([{"label": "PDF", "name": "paper.pdf", "url": "u"}], v))),
            mock.patch("app.rag.stats", lambda tid: {"chunks": 5}),
            mock.patch("app.db.update_thread", upd),
        ]

    def __enter__(self):
        for p in self.patches:
            p.start()
        return self

    def __exit__(self, *a):
        for p in self.patches:
            p.stop()


class LegacyStages(unittest.TestCase):
    def test_full_run_reaches_ready(self):
        with Harness(self) as h:
            j = FakeJob()
            pipeline.run_create(j, "t1", "topic", "ieee")
            self.assertEqual(h.calls, ["plan", "discover", "read", "bib", "draft", "build", "review", "build", "export"])
            self.assertEqual(h.thread["phase"], "ready")
            self.assertTrue(j.done and not j.error)

    def test_no_sources_fails_early(self):
        with Harness(self, index_n=0) as h:
            j = FakeJob()
            pipeline.run_create(j, "t1", "topic", "ieee")
            self.assertEqual(h.thread["phase"], "failed_early")
            self.assertNotIn("read", h.calls)

    def test_unverified_review_never_becomes_ready_and_never_exports_final(self):
        with Harness(self, review_ok=False) as h:
            j = FakeJob()
            pipeline.run_create(j, "t1", "topic", "ieee")
            self.assertEqual(h.thread["phase"], "review_paused")
            self.assertNotIn("ready", h.phases)
            self.assertNotIn("export", h.calls)


@unittest.skipUnless(HAVE_LG, "langgraph not installed")
class GraphStages(unittest.TestCase):
    def run_graph(self, h, text="write a literature review on graph neural networks"):
        j = FakeJob()
        jobs.RUNNING["t1"] = j
        graph.set_graph(graph.build(InMemorySaver()))

        def boom():
            raise llm.HostedCallsDisabled("off")

        with mock.patch.object(llm, "factory", boom), mock.patch("app.scope.clarify", lambda t: False):
            graph.run(j, "t1", text, "ieee")
        jobs.RUNNING.pop("t1", None)
        return j

    def test_same_stage_sequence_as_legacy(self):
        with Harness(self) as h:
            j = self.run_graph(h)
            self.assertEqual(h.calls, ["plan", "discover", "read", "bib", "draft", "build", "review", "build", "export"])
            self.assertEqual(h.thread["phase"], "ready")

    def test_graph_stops_at_failed_stage_and_never_marks_ready(self):
        with Harness(self, review_ok=False) as h:
            j = self.run_graph(h)
            self.assertEqual(h.thread["phase"], "review_paused")
            self.assertNotIn("export", h.calls)
            self.assertNotIn("ready", h.phases)

    def test_graph_no_sources(self):
        with Harness(self, index_n=0) as h:
            self.run_graph(h)
            self.assertEqual(h.thread["phase"], "failed_early")
            self.assertNotIn("draft", h.calls)

    def test_write_node_refuses_when_paper_in_progress(self):
        with Harness(self) as h:
            h.thread["phase"] = "reading_paused"
            j = FakeJob()
            jobs.RUNNING["t1"] = j
            out = graph.write_paper({"tid": "t1", "text": "x", "template": "ieee"})
            jobs.RUNNING.pop("t1", None)
            self.assertEqual(out, {"go": False})
            self.assertEqual(h.calls, [])
            self.assertTrue(j.done)


if __name__ == "__main__":
    unittest.main()
