"""Operational outcomes (timeout/transport/interruption) are typed, durable and never a verdict. No hosted calls."""

import json, os, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import httpx
from app import span_review, structured, evidence
from app.continuation import BudgetProgress, continue_budgeted


class Job:
    def __init__(self):
        self.lines = []

    def tool_start(self, *a):
        return "x"

    def tool_done(self, *a, **kw):
        pass

    def text(self, t):
        self.lines.append(t)


SCHEMA = {
    "type": "object",
    "properties": {"status": {"type": "string", "enum": ["supported", "unsupported"]}},
    "required": ["status"],
    "additionalProperties": False,
}


class FakeResp:
    def __init__(self, data=None, status=200):
        self.data = data if data is not None else {}
        self.status = status

    def raise_for_status(self):
        if self.status >= 400:
            raise httpx.HTTPStatusError(
                "x",
                request=httpx.Request("POST", "http://x"),
                response=httpx.Response(self.status),
            )

    def json(self):
        return self.data


class FakeProc:
    def __init__(self, alive=True):
        self.alive = alive

    def poll(self):
        return None if self.alive else 1

    def terminate(self):
        pass

    def wait(self, timeout=None):
        return 0

    def kill(self):
        pass


def fake_client(second):
    class C:
        def __init__(self, *a, **k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def get(self, *a, **k):
            return FakeResp()

        def post(self, url, **k):
            if url == "/session":
                return FakeResp({"id": "s1"})
            if isinstance(second, Exception):
                raise second
            return second

    return C


def run_stage(second, alive=True):
    with tempfile.TemporaryDirectory() as td:
        cwd = Path(td)
        (cwd / "opencode.json").write_text('{"agent":{"paperforge":{}}}')
        with patch.object(
            structured.subprocess, "Popen", return_value=FakeProc(alive)
        ), patch.object(structured.httpx, "Client", fake_client(second)):
            return structured.run(cwd, "p", SCHEMA, timeout=5)


class StructuredTypedOutcomeTests(unittest.TestCase):
    def code(self, second, alive=True):
        text, ok, _, events = run_stage(second, alive)
        self.assertFalse(ok)
        self.assertEqual(text, "")
        return structured.outcome_code(events)

    def test_each_operational_failure_has_its_own_code(self):
        self.assertEqual(self.code(httpx.ReadTimeout("slow")), "timeout")
        self.assertEqual(self.code(httpx.ConnectError("down")), "transport_error")
        self.assertEqual(self.code(FakeResp(status=429)), "http_error")
        self.assertEqual(
            self.code(FakeResp({"info": {"error": {"name": "x"}}})), "native_error"
        )
        self.assertEqual(self.code(FakeResp({"info": {}})), "empty")
        self.assertEqual(
            self.code(FakeResp({"info": {"structured": {"status": "maybe"}}})),
            "schema_invalid",
        )
        self.assertEqual(self.code(FakeResp(), alive=False), "server_exit")

    def test_success_is_ok(self):
        text, ok, _, events = run_stage(
            FakeResp({"info": {"structured": {"status": "supported"}}})
        )
        self.assertTrue(ok)
        self.assertEqual(structured.outcome_code(events), "ok")
        self.assertEqual(json.loads(text), {"status": "supported"})

    def test_timeout_message_is_not_a_semantic_message(self):
        _, _, _, events = run_stage(httpx.ReadTimeout("slow"))
        self.assertTrue(all("unsupported" not in e.get("message", "") for e in events))


class ReviewOneMappingTests(unittest.TestCase):
    def test_timeout_maps_to_operational_not_invalid_response(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with patch.object(span_review, "candidates", return_value=[]), patch.object(
                span_review.opencode,
                "write_config",
                side_effect=lambda w, *a: (w / "opencode.json").write_text(
                    '{"agent":{"paperforge":{}}}'
                ),
            ), patch.object(
                span_review.structured,
                "run",
                return_value=(
                    "",
                    False,
                    None,
                    [
                        {"kind": "error", "code": "timeout", "message": "x"},
                        {"kind": "done", "ok": False},
                    ],
                ),
            ):
                entries, failures = span_review.review_one(
                    root, 1, "A claim sentence with enough words.", [], []
                )
        self.assertEqual(entries, [])
        self.assertEqual(len(failures), 1)
        self.assertTrue(span_review.is_operational(failures[0]))
        self.assertIn("operational timeout", failures[0])
        self.assertNotIn("invalid review response", failures[0])
        self.assertNotIn("unsupported", failures[0].split("operational")[0])


def setup(
    td,
    text="A sufficiently long source finding that the reviewer will be asked about. ",
):
    root = Path(td)
    (root / "paper").mkdir()
    (root / "paper/main.tex").write_text(r"\maketitle" + "\n" + text + r"\cite{k}")
    source = root / "source.txt"
    source.write_text(
        "=== PAGE 1 ===\n" + "A narrow supported method is described. " * 8
    )
    return root, [{"key": "k", "status": "indexed", "text_path": str(source)}]


OP = [
    "Span1: operational timeout: the review call returned no usable result; this is not a verdict on the claim"
]


class ReviewAllOperationalTests(unittest.TestCase):
    def run_all(self, root, rows, judge, env=None):
        with patch.dict(
            os.environ, env or {"PAPERFORGE_REVIEW_NEW_ATTEMPT": ""}
        ), patch.object(span_review.db, "sources", return_value=rows), patch.object(
            span_review.opencode,
            "write_config",
            side_effect=lambda w, *a: (w / "opencode.json").write_text(
                '{"agent":{"paperforge":{}}}'
            ),
        ), patch.object(
            evidence, "validate", return_value=[]
        ):
            return span_review.review_all(Job(), "t", root, [])

    def test_timeout_is_recorded_durably_and_is_not_a_rejection_or_ready(self):
        with tempfile.TemporaryDirectory() as td:
            root, rows = setup(td)
            with patch.object(
                span_review, "review_one", return_value=([], OP)
            ) as judge:
                self.assertFalse(self.run_all(root, rows, judge))
                self.assertEqual(judge.call_count, 1)
            self.assertFalse((root / "span-review/rejected-spans.json").exists())
            self.assertFalse((root / "span-review/unresolved-spans.json").exists())
            led = json.loads((root / "span-review/operational-spans.json").read_text())
            self.assertEqual(len(led), 1)
            self.assertEqual(list(led.values())[0]["code"], "timeout")
            recs = [
                json.loads(l)
                for l in (root / "span-review/outcomes.jsonl").read_text().splitlines()
            ]
            self.assertEqual([r["event"] for r in recs], ["start", "end"])
            self.assertEqual(recs[1]["outcome"], "operational")
            self.assertEqual(recs[1]["code"], "timeout")
            self.assertEqual(recs[0]["attempt"], recs[1]["attempt"])
            claim = json.loads((root / "claim-review.json").read_text())
            self.assertEqual(claim["claims"], [])
            fb = json.loads((root / "review-feedback.json").read_text())
            self.assertEqual(fb["errors"], OP)
            self.assertEqual(fb["spans_complete"], 0)

    def test_ordinary_resume_never_reissues_but_explicit_attempt_does_and_keeps_history(
        self,
    ):
        with tempfile.TemporaryDirectory() as td:
            root, rows = setup(td)
            with patch.object(
                span_review, "review_one", return_value=([], OP)
            ) as judge:
                self.assertFalse(self.run_all(root, rows, judge))
                for _ in range(3):
                    self.assertFalse(self.run_all(root, rows, judge))
                self.assertEqual(judge.call_count, 1)
                self.assertFalse(
                    self.run_all(
                        root, rows, judge, {"PAPERFORGE_REVIEW_NEW_ATTEMPT": "a2"}
                    )
                )
                self.assertEqual(judge.call_count, 2)
                self.assertFalse(
                    self.run_all(
                        root, rows, judge, {"PAPERFORGE_REVIEW_NEW_ATTEMPT": "a2"}
                    )
                )
                self.assertEqual(judge.call_count, 2)
            v = list(
                json.loads(
                    (root / "span-review/operational-spans.json").read_text()
                ).values()
            )[0]
            self.assertEqual(v["token"], "a2")
            self.assertEqual(v["history"][0]["code"], "timeout")

    def test_interrupted_call_is_detected_and_not_reissued(self):
        with tempfile.TemporaryDirectory() as td:
            root, rows = setup(td)
            import hashlib

            source_hash = hashlib.sha256(
                ("span-v6" + Path(rows[0]["text_path"]).read_text()).encode()
            ).hexdigest()
            block = span_review.spans((root / "paper/main.tex").read_text())[0]
            ck = hashlib.sha256((source_hash + block).encode()).hexdigest()
            (root / "span-review").mkdir()
            (root / "span-review/outcomes.jsonl").write_text(
                json.dumps(
                    {
                        "event": "start",
                        "attempt": "dead1",
                        "span": 1,
                        "cache_key": ck,
                        "token": "",
                        "contract": "span-v6",
                        "ts": 1,
                    }
                )
                + "\n"
            )
            with patch.object(
                span_review, "review_one", return_value=([{"draft_quote": block}], [])
            ) as judge:
                self.assertFalse(self.run_all(root, rows, judge))
                self.assertEqual(judge.call_count, 0)
                self.assertFalse(self.run_all(root, rows, judge))
                self.assertEqual(judge.call_count, 0)
            recs = [
                json.loads(l)
                for l in (root / "span-review/outcomes.jsonl").read_text().splitlines()
            ]
            self.assertEqual([r["event"] for r in recs], ["start", "interrupted"])
            fb = json.loads((root / "review-feedback.json").read_text())
            self.assertIn("operational interrupted", fb["errors"][0])
            with patch.object(
                span_review,
                "review_one",
                return_value=(
                    [
                        {
                            "draft_quote": block,
                            "claim": block,
                            "source_key": "k",
                            "page": 1,
                            "quote": "q",
                            "status": "supported",
                        }
                    ],
                    [],
                ),
            ) as judge:
                self.assertTrue(
                    self.run_all(
                        root, rows, judge, {"PAPERFORGE_REVIEW_NEW_ATTEMPT": "again"}
                    )
                )
                self.assertEqual(judge.call_count, 1)
            self.assertEqual(
                json.loads((root / "span-review/operational-spans.json").read_text()),
                {},
            )

    def test_exception_in_call_is_recorded_as_operational_not_lost(self):
        with tempfile.TemporaryDirectory() as td:
            root, rows = setup(td)
            with patch.object(
                span_review, "review_one", side_effect=RuntimeError("boom")
            ) as judge:
                self.assertFalse(self.run_all(root, rows, judge))
            recs = [
                json.loads(l)
                for l in (root / "span-review/outcomes.jsonl").read_text().splitlines()
            ]
            self.assertEqual(recs[-1]["outcome"], "operational")
            self.assertFalse((root / "span-review/rejected-spans.json").exists())

    def test_semantic_rejection_history_is_unaffected_and_operational_never_overrides_it(
        self,
    ):
        with tempfile.TemporaryDirectory() as td:
            root, rows = setup(td)
            with patch.object(
                span_review.opencode, "run_text", return_value=("", False, None, [])
            ), patch.object(
                span_review.structured, "run", return_value=("", False, None, [])
            ), patch.object(
                span_review,
                "review_one",
                return_value=([], ["Span1: overbroad outcome"]),
            ) as judge:
                self.assertFalse(self.run_all(root, rows, judge))
                self.assertEqual(judge.call_count, 1)
                rej = json.loads((root / "span-review/rejected-spans.json").read_text())
                self.assertEqual(len(rej), 1)
                judge.return_value = ([], OP)
                self.assertFalse(self.run_all(root, rows, judge))
                self.assertEqual(judge.call_count, 1)
            self.assertEqual(
                json.loads((root / "span-review/rejected-spans.json").read_text()), rej
            )
            self.assertFalse((root / "span-review/operational-spans.json").exists())

    def test_unresolved_semantic_retention_still_holds_alongside(self):
        unres = [
            "Span1: unresolved clause grounding: a clause is not copied exactly; supported verdict not verifiable"
        ]
        with tempfile.TemporaryDirectory() as td:
            root, rows = setup(td)
            with patch.object(
                span_review, "review_one", return_value=([], unres)
            ) as judge:
                self.assertFalse(self.run_all(root, rows, judge))
                judge.return_value = ([], OP)
                for _ in range(2):
                    self.assertFalse(self.run_all(root, rows, judge))
                self.assertEqual(judge.call_count, 1)
            self.assertFalse((root / "span-review/operational-spans.json").exists())

    def test_failed_span_stops_review_without_calling_later_spans(self):
        with tempfile.TemporaryDirectory() as td:
            root, rows = setup(td)
            blocks = [
                "First sufficiently long claim sentence for review. \\cite{k}",
                "Second sufficiently long claim sentence for review. \\cite{k}",
            ]
            with patch.object(span_review, "spans", return_value=blocks), patch.object(
                span_review, "review_one", return_value=([], OP)
            ) as judge:
                self.assertFalse(self.run_all(root, rows, judge))
                self.assertEqual(judge.call_count, 1)


class SliceGuardTests(unittest.TestCase):
    """A fake clock advances 30s per review call; slice 100s with an 80s timeout fits exactly one call."""

    def setUp(self):
        self.blocks = [
            "First sufficiently long claim sentence for review.",
            "Second sufficiently long claim sentence for review.",
            "Third sufficiently long claim sentence for review.",
        ]
        self.t = 0.0

    def review(self, root, i, block, *a):
        self.t += 30.0
        return [
            {
                "draft_quote": block,
                "claim": block,
                "source_key": "k",
                "page": 1,
                "quote": "q",
                "status": "supported",
            }
        ], []

    def env(self, slice_s="100"):
        e = {"PAPERFORGE_REVIEW_NEW_ATTEMPT": ""}
        if slice_s is not None:
            e["PAPERFORGE_REVIEW_SLICE_SECONDS"] = slice_s
        return e

    def test_guard_stops_after_one_span_and_does_not_continue_in_process(self):
        with tempfile.TemporaryDirectory() as td:
            root, rows = setup(td)
            job = Job()
            with patch.dict(os.environ, self.env()), patch.object(
                span_review.db, "sources", return_value=rows
            ), patch.object(
                span_review, "spans", return_value=self.blocks
            ), patch.object(
                span_review.time, "monotonic", side_effect=lambda: self.t
            ), patch.object(
                span_review, "review_one", side_effect=self.review
            ) as judge, patch.object(
                evidence, "validate", return_value=[]
            ):
                result = continue_budgeted(
                    lambda: span_review.review_all(job, "t", root, [], timeout=80), job
                )
            self.assertIsNone(result)
            self.assertEqual(judge.call_count, 1)
            self.assertTrue(any("Slice time guard" in l for l in job.lines))
            fb = json.loads((root / "review-feedback.json").read_text())
            self.assertEqual(fb["spans_complete"], 1)
            self.assertEqual(fb["spans_total"], 3)
            self.assertEqual(fb["errors"], [span_review.GUARD_ERROR])

    def test_explicit_resume_advances_one_span_each_and_completes_only_when_all_done(
        self,
    ):
        with tempfile.TemporaryDirectory() as td:
            root, rows = setup(td)
            outcomes = []
            with patch.dict(os.environ, self.env()), patch.object(
                span_review.db, "sources", return_value=rows
            ), patch.object(
                span_review, "spans", return_value=self.blocks
            ), patch.object(
                span_review.time, "monotonic", side_effect=lambda: self.t
            ), patch.object(
                span_review, "review_one", side_effect=self.review
            ) as judge, patch.object(
                evidence, "validate", return_value=[]
            ):
                for _ in range(3):
                    self.t = 0.0
                    job = Job()
                    outcomes.append(
                        continue_budgeted(
                            lambda: span_review.review_all(
                                job, "t", root, [], timeout=80
                            ),
                            job,
                        )
                    )
            self.assertEqual(outcomes, [None, None, True])
            self.assertEqual(judge.call_count, 3)

    def test_guard_off_by_default_keeps_existing_behaviour(self):
        with tempfile.TemporaryDirectory() as td:
            root, rows = setup(td)
            job = Job()
            with patch.dict(os.environ, self.env(None)), patch.object(
                span_review.db, "sources", return_value=rows
            ), patch.object(
                span_review, "spans", return_value=self.blocks
            ), patch.object(
                span_review.time, "monotonic", side_effect=lambda: self.t
            ), patch.object(
                span_review, "review_one", side_effect=self.review
            ) as judge, patch.object(
                evidence, "validate", return_value=[]
            ):
                os.environ.pop("PAPERFORGE_REVIEW_SLICE_SECONDS", None)
                self.assertTrue(
                    continue_budgeted(
                        lambda: span_review.review_all(job, "t", root, [], timeout=80),
                        job,
                    )
                )
            self.assertEqual(judge.call_count, 3)


class SliceConfigTests(unittest.TestCase):
    def go(self, env, clock=None, blocks=None):
        blocks = blocks or ["First sufficiently long claim sentence for review."]
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root, rows = setup(td.name)
        job = Job()
        patches = [
            patch.dict(os.environ, {"PAPERFORGE_REVIEW_NEW_ATTEMPT": "", **env}),
            patch.object(span_review.db, "sources", return_value=rows),
            patch.object(span_review, "spans", return_value=blocks),
            patch.object(evidence, "validate", return_value=[]),
        ]
        if clock:
            patches.append(
                patch.object(span_review.time, "monotonic", side_effect=clock)
            )
        judge = patch.object(span_review, "review_one", return_value=([], []))
        with judge as j:
            for pt in patches:
                pt.start()
            try:
                result = continue_budgeted(
                    lambda: span_review.review_all(job, "t", root, [], timeout=80), job
                )
            finally:
                for pt in patches:
                    pt.stop()
        return root, job, result, j

    def test_slice_shorter_than_timeout_fails_clearly_without_a_call(self):
        root, job, result, j = self.go({"PAPERFORGE_REVIEW_SLICE_SECONDS": "60"})
        self.assertFalse(result)
        self.assertEqual(j.call_count, 0)
        fb = json.loads((root / "review-feedback.json").read_text())
        self.assertEqual(len(fb["errors"]), 1)
        self.assertTrue(fb["errors"][0].startswith("Invalid slice configuration"))
        self.assertFalse(any("Continuing" in l for l in job.lines))
        self.assertFalse((root / "span-review/outcomes.jsonl").exists())

    def test_slice_equal_to_timeout_with_any_elapsed_startup_fails_without_a_call(self):
        ticks = iter([0.0, 5.0] + [5.0] * 50)
        root, job, result, j = self.go(
            {"PAPERFORGE_REVIEW_SLICE_SECONDS": "80"}, clock=lambda: next(ticks)
        )
        self.assertFalse(result)
        self.assertEqual(j.call_count, 0)
        self.assertTrue(
            json.loads((root / "review-feedback.json").read_text())["errors"][
                0
            ].startswith("Invalid slice configuration")
        )

    def test_startup_headroom_consumed_blocks_first_call(self):
        ticks = iter(
            [0.0] + [30.0] * 50
        )  # 30s spent before the first call; 100s slice cannot hold 30+80
        root, job, result, j = self.go(
            {"PAPERFORGE_REVIEW_SLICE_SECONDS": "100"}, clock=lambda: next(ticks)
        )
        self.assertEqual(j.call_count, 0)
        self.assertIn(
            "30.0s already elapsed",
            json.loads((root / "review-feedback.json").read_text())["errors"][0],
        )

    def test_slice_that_fits_one_call_runs_exactly_one(self):
        ticks = iter([0.0, 1.0] + [60.0] * 50)
        root, job, result, j = self.go(
            {"PAPERFORGE_REVIEW_SLICE_SECONDS": "100"},
            clock=lambda: next(ticks),
            blocks=[
                "First sufficiently long claim sentence for review.",
                "Second sufficiently long claim sentence for review.",
            ],
        )
        self.assertEqual(j.call_count, 1)
        self.assertEqual(
            json.loads((root / "review-feedback.json").read_text())["errors"],
            [span_review.GUARD_ERROR],
        )

    def test_invalid_slice_never_spins_budget_progress(self):
        root, job, result, j = self.go({"PAPERFORGE_REVIEW_SLICE_SECONDS": "10"})
        self.assertEqual(j.call_count, 0)
        self.assertFalse(any("saved" in l for l in job.lines))


class InterruptedScopeTests(unittest.TestCase):
    def stale(self, root, rows, block, token=""):
        import hashlib

        sh = hashlib.sha256(
            ("span-v6" + Path(rows[0]["text_path"]).read_text()).encode()
        ).hexdigest()
        ck = hashlib.sha256((sh + block).encode()).hexdigest()
        (root / "span-review").mkdir(exist_ok=True)
        (root / "span-review/outcomes.jsonl").write_text(
            json.dumps(
                {
                    "event": "start",
                    "attempt": "dead1",
                    "span": 1,
                    "cache_key": ck,
                    "token": token,
                    "contract": "span-v6",
                    "ts": 1,
                }
            )
            + "\n"
        )

    def go(self, root, rows, env=None):
        with patch.dict(
            os.environ, env or {"PAPERFORGE_REVIEW_NEW_ATTEMPT": ""}
        ), patch.object(span_review.db, "sources", return_value=rows), patch.object(
            evidence, "validate", return_value=[]
        ), patch.object(
            span_review.opencode,
            "write_config",
            side_effect=lambda w, *a: (w / "opencode.json").write_text(
                '{"agent":{"paperforge":{}}}'
            ),
        ), patch.object(
            span_review, "review_one", return_value=([{"draft_quote": "x"}], [])
        ) as j:
            span_review.review_all(Job(), "t", root, [])
            return j.call_count

    def test_changed_claim_does_not_inherit_the_stale_block(self):
        with tempfile.TemporaryDirectory() as td:
            root, rows = setup(td)
            old = span_review.spans((root / "paper/main.tex").read_text())[0]
            self.stale(root, rows, old)
            self.assertEqual(self.go(root, rows), 0)
            (root / "paper/main.tex").write_text(
                r"\maketitle"
                + "\n"
                + "A changed and sufficiently long claim about the narrow method described. "
                + r"\cite{k}"
            )
            self.assertEqual(self.go(root, rows), 1)

    def test_changed_source_does_not_inherit_the_stale_block(self):
        with tempfile.TemporaryDirectory() as td:
            root, rows = setup(td)
            old = span_review.spans((root / "paper/main.tex").read_text())[0]
            self.stale(root, rows, old)
            self.assertEqual(self.go(root, rows), 0)
            Path(rows[0]["text_path"]).write_text(
                "=== PAGE 1 ===\n"
                + "A different narrow supported method is described. " * 8
            )
            self.assertEqual(self.go(root, rows), 1)

    def test_explicit_new_token_allows_same_inputs(self):
        with tempfile.TemporaryDirectory() as td:
            root, rows = setup(td)
            old = span_review.spans((root / "paper/main.tex").read_text())[0]
            self.stale(root, rows, old)
            self.assertEqual(self.go(root, rows), 0)
            self.assertEqual(
                self.go(root, rows, {"PAPERFORGE_REVIEW_NEW_ATTEMPT": "t2"}), 1
            )

    def test_start_records_carry_claim_source_contract_and_token(self):
        with tempfile.TemporaryDirectory() as td:
            root, rows = setup(td)
            self.go(root, rows, {"PAPERFORGE_REVIEW_NEW_ATTEMPT": "tk"})
            st = json.loads(
                (root / "span-review/outcomes.jsonl").read_text().splitlines()[0]
            )
            for k in (
                "cache_key",
                "token",
                "contract",
                "source_sha256",
                "block_sha256",
            ):
                self.assertIn(k, st)
            self.assertEqual((st["contract"], st["token"]), ("span-v6", "tk"))


class ContinuationHaltTests(unittest.TestCase):
    def test_halt_never_continues_automatically(self):
        calls = []

        def step():
            calls.append(1)
            raise BudgetProgress("review", 1, 3, halt=True)

        job = Job()
        self.assertIsNone(continue_budgeted(step, job))
        self.assertEqual(len(calls), 1)

    def test_plain_budget_progress_still_continues(self):
        calls = []

        def step():
            calls.append(1)
            if len(calls) < 3:
                raise BudgetProgress("review", len(calls), 3)
            return True

        self.assertTrue(continue_budgeted(step, Job()))
        self.assertEqual(len(calls), 3)


if __name__ == "__main__":
    unittest.main()
