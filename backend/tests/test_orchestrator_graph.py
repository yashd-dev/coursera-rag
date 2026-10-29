import unittest
from unittest import mock

try:
    from langchain_core.messages import AIMessage
    from langgraph.checkpoint.memory import InMemorySaver
    from app.orchestrator import graph, intents, llm
    HAVE_LG = True
except ImportError:  # legacy installs without LangChain skip these tests
    HAVE_LG = False

from app import jobs


class FakeJob:
    def __init__(self):
        self.out, self.done, self.parts, self.tools = [], False, [], []

    def text(self, s):
        self.out.append(s)

    def tool_start(self, n, a):
        self.tools.append(n)
        return n

    def tool_done(self, *a, **k):
        pass

    def finish(self, error=None):
        self.done = True


class FakeModel:
    """Stub chat model. script maps bound-tool name -> AIMessage factory."""

    def __init__(self, script):
        self.script, self.bound, self.calls = script, [], 0

    def bind_tools(self, tools, tool_choice=None):
        c = FakeModel(self.script)
        c.bound = [getattr(t, "name", str(t)) for t in tools]
        c.parent = self
        return c

    def invoke(self, msgs):
        self.parent.calls += 1
        return self.script(self.bound, msgs, self.parent.calls)


def stub_script(intent="ask", search=True):
    def f(bound, msgs, n):
        if bound == ["Intent"]:
            return AIMessage(content="", tool_calls=[{"name": "Intent", "args": {"intent": intent, "confidence": 0.9}, "id": "i1"}])
        if search and n < 4 and not any(m.__class__.__name__ == "ToolMessage" for m in msgs):
            return AIMessage(content="", tool_calls=[{"name": "search_arxiv", "args": {"query": "graph rag"}, "id": "t1"}])
        return AIMessage(content="done")
    return f


THREAD = {"phase": "new", "template": "ieee", "custom": {}}


@unittest.skipUnless(HAVE_LG, "langgraph not installed")
class GraphTests(unittest.TestCase):
    def setUp(self):
        self.job = FakeJob()
        jobs.RUNNING["t1"] = self.job
        graph.set_graph(graph.build(InMemorySaver()))
        self.created, self.asked = [], []
        self.thread = dict(THREAD)
        self.patches = [
            mock.patch("app.db.get_thread", lambda tid: self.thread),
            mock.patch("app.pipeline.create_prelude", lambda j, tid, t, tpl: (self.created.append(t), None)[1]),
            mock.patch("app.pipeline.run_ask", lambda j, tid, t, note: (self.asked.append(t), j.finish())),
            mock.patch("app.pipeline.run_scope", lambda j, tid, t: j.finish()),
            mock.patch("app.research.search_arxiv", lambda q, n=8, recent=False: [dict(title="Paper A", year=2024, venue="arXiv", url="http://a", pdf_url="p", origin="arxiv", authors="X")]),
            mock.patch("app.research.search_openalex", lambda q, n=8, recent=False: []),
            mock.patch("app.scope.clarify", lambda t: False),
        ]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        jobs.RUNNING.pop("t1", None)

    def go(self, text, model=None, job=None):
        if job:
            self.job = job
            jobs.RUNNING["t1"] = job
        m = model or FakeModel(stub_script())
        with mock.patch.object(llm, "factory", lambda: m):
            graph.run(self.job, "t1", text, "ieee")
        return m

    def test_find_papers_executes_tools_in_graph_and_never_writes(self):
        m = self.go("find me some papers on graph rag", FakeModel(stub_script("find_papers")))
        self.assertEqual(self.created, [])
        self.assertIn("search_arxiv", self.job.tools)  # graph executed the model's tool call
        self.assertTrue(any("Paper A" in o for o in self.job.out))
        self.assertTrue(any("Nothing was downloaded" in o for o in self.job.out))

    def test_find_without_model_still_searches_only(self):
        def boom():
            raise llm.HostedCallsDisabled("off")
        with mock.patch.object(llm, "factory", boom):
            graph.run(self.job, "t1", "search for papers on diffusion", "ieee")
        self.assertEqual(self.created, [])
        self.assertTrue(any("Paper A" in o for o in self.job.out))

    def test_model_saying_write_for_a_search_phrase_is_overridden(self):
        self.go("find papers about lora", FakeModel(stub_script("write_paper")))
        self.assertEqual(self.created, [])

    def test_unknown_intent_clarifies_without_writing(self):
        def boom():
            raise RuntimeError("down")
        with mock.patch.object(llm, "factory", boom):
            graph.run(self.job, "t1", "hmm graphs", "ieee")
        self.assertEqual(self.created, [])
        self.assertTrue(any("not sure" in o for o in self.job.out))

    def test_explicit_write_needs_no_extra_prompt(self):
        self.go("write a literature review on graph rag", FakeModel(stub_script("write_paper", search=False)))
        self.assertEqual(len(self.created), 1)

    def test_model_only_write_asks_then_yes_starts_once(self):
        self.go("graph rag for contracts please do it", FakeModel(stub_script("write_paper", search=False)))
        self.assertEqual(self.created, [])  # cannot start without a resume value
        self.assertTrue(any("Reply yes" in o for o in self.job.out))
        j2 = FakeJob()
        self.go("yes", job=j2)
        self.assertEqual(len(self.created), 1)
        j3 = FakeJob()
        self.go("yes", job=j3)  # replay must not start a second run
        self.assertEqual(len(self.created), 1)

    def test_consent_no_cancels(self):
        self.go("graph rag for contracts please do it", FakeModel(stub_script("write_paper", search=False)))
        self.go("no", job=FakeJob())
        self.assertEqual(self.created, [])

    def test_other_reply_cancels_pending_and_is_routed_fresh(self):
        self.go("graph rag for contracts please do it", FakeModel(stub_script("write_paper", search=False)))
        j2 = FakeJob()
        self.go("what is graph rag?", job=j2)
        self.assertEqual(self.created, [])
        self.assertEqual(self.asked, ["what is graph rag?"])

    def test_questions_and_commands_use_no_model(self):
        m = FakeModel(stub_script())
        self.thread["phase"] = "ready"
        self.go("/ask what is the main result?", m)
        self.assertEqual(m.calls, 0)
        self.assertEqual(len(self.asked), 1)

    def test_write_skipped_when_paper_already_in_progress(self):
        self.thread["phase"] = "review_paused"
        edits = []
        with mock.patch("app.pipeline.run_edit", lambda j, tid, t, original=None: (edits.append(t), j.finish())):
            self.go("write a literature review on graph rag")  # existing paper: handled as an edit request, never a new run
        self.assertEqual(self.created, [])
        self.assertEqual(len(edits), 1)


@unittest.skipUnless(HAVE_LG, "langgraph not installed")
class IntentTable(unittest.TestCase):
    CASES = [
        ("find papers on graph rag", "find_papers"), ("Find me papers about LoRA", "find_papers"),
        ("search for articles on diffusion models", "find_papers"), ("look up surveys on RAG", "find_papers"),
        ("suggest some papers for transformers", "find_papers"), ("recommend literature on causal inference", "find_papers"),
        ("show me studies on retrieval", "find_papers"), ("get me references about GNNs", "find_papers"),
        ("list papers on agents", "find_papers"), ("search papers: multimodal RAG", "find_papers"),
        ("find sources on bias in LLMs", "find_papers"), ("look for research papers on RLHF", "find_papers"),
        ("write a literature review on graph rag", "write_paper"), ("draft a research paper on LoRA", "write_paper"),
        ("generate a survey on diffusion models", "write_paper"), ("compose the paper on agents", "write_paper"),
        ("create a review paper on RAG", "write_paper"), ("prepare a manuscript about GNNs", "write_paper"),
        ("write my paper on retrieval", "write_paper"), ("produce an article on causal LLMs", "write_paper"),
        ("write a paper on bias in LLMs", "write_paper"), ("draft the literature review on RLHF", "write_paper"),
        ("/write graph rag", "write_paper"), ("/find graph rag", "find_papers"), ("/ask what is x", "ask"),
        ("find papers and write a literature review on RAG", "find_papers" if False else "write_paper"),
    ]

    def test_table(self):
        for text, want in self.CASES:
            with self.subTest(text=text):
                self.assertEqual(intents.guard(text, None)[0], want)

    def test_only_explicit_phrases_skip_consent(self):
        self.assertTrue(intents.guard("write a literature review on rag", None)[1])
        self.assertFalse(intents.guard("find papers and write a literature review on RAG", None)[1])
        self.assertFalse(intents.guard("graph rag stuff", "write_paper")[1])

    def test_unknown_goes_to_clarify(self):
        for t in ["hmm", "graphs", "rag", "something about llms", "ok then", "maybe", "papers", "thoughts?", "idk", "tell"]:
            with self.subTest(t=t):
                self.assertEqual(intents.guard(t, None)[0], "clarify")

    def test_consent(self):
        for t in ["yes", "Yes go ahead", "ok", "sure", "proceed", "do it"]:
            self.assertEqual(intents.consent_decision(t), "yes")
        for t in ["no", "cancel", "stop", "don't", "not now"]:
            self.assertEqual(intents.consent_decision(t), "no")
        self.assertEqual(intents.consent_decision("what is rag?"), "other")


if __name__ == "__main__":
    unittest.main()
