import unittest
from app import span_review
from app.span_review import spans


class SpanTests(unittest.TestCase):
    def test_exact_sentence_spans(self):
        text = (
            r"\maketitle"
            + "\n"
            + r"\section{Test}"
            + "\nThis is a specific sentence with enough words to review. Another specific sentence is independently checked using exact source evidence.\n"
            + r"\bibliographystyle{x}"
        )
        s = spans(text)
        self.assertEqual(len(s), 2)
        self.assertTrue(all(x in text for x in s))

    def test_adjacent_keywords_and_table_do_not_hide_prose(self):
        text = (
            r"\maketitle"
            + "\n"
            + r"\begin{abstract}"
            + "\nA sufficiently long abstract sentence describes the actual paper and evidence.\n"
            + r"\end{abstract}"
            + "\n"
            + r"\begin{IEEEkeywords}retrieval\end{IEEEkeywords}"
            + "\n"
            + r"\section{Review}"
            + "\nThe source summary must also be checked even without blank lines.\n"
            + r"\begin{table}"
            + "\nSource & Approach & Evaluation \\\nAuthor & This is the approach & This is the evaluation \\\n"
            + r"\end{table}"
            + "\n"
            + r"\bibliographystyle{x}"
        )
        rows = spans(text)
        self.assertEqual(len(rows), 3)
        self.assertTrue(all(row in text for row in rows))


class TableRepairTests(unittest.TestCase):
    def test_cell_repair_preserves_source(self):
        row = r"Hossain 2026 \cite{hossain2026core} & method & bad finding \\ \hline"
        fixed = span_review.repair_table_row(
            row, ["Wrong author", "k-core decomposition", "Global QA comparison"]
        )
        self.assertTrue(fixed.startswith(r"Hossain 2026 \cite{hossain2026core} &"))
        self.assertIn("Global QA comparison", fixed)
        self.assertEqual(fixed.count("&"), 2)
        self.assertTrue(fixed.endswith(r"\\ \hline"))

    def test_reject_injected_structure(self):
        with self.assertRaises(ValueError):
            span_review.repair_table_row("a & b & c", ["a", r"\end{table}", "c"])


class RejectionTests(unittest.TestCase):
    def test_rejected_span_cannot_pass_unchanged_retry(self):
        import tempfile, json
        from pathlib import Path
        from unittest.mock import patch

        class Job:
            def tool_start(self, *a):
                return "x"

            def tool_done(self, *a, **kw):
                pass

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "paper").mkdir()
            (root / "paper/main.tex").write_text(
                r"\maketitle"
                + "\n"
                + "A sufficiently long source finding with a disputed broad outcome. "
                + r"\cite{k}"
            )
            source = root / "source.txt"
            source.write_text(
                "=== PAGE 1 ===\n" + "A narrow supported method is described. " * 8
            )
            rows = [{"key": "k", "status": "indexed", "text_path": str(source)}]
            with patch.object(
                span_review.db, "sources", return_value=rows
            ), patch.object(
                span_review.opencode,
                "write_config",
                side_effect=lambda work, *a: (work / "opencode.json").write_text(
                    '{"agent":{"paperforge":{}}}'
                ),
            ), patch.object(
                span_review.opencode,
                "run_text",
                return_value=(
                    '{"replacement":"unchanged invalid repair with \\\\bad"}',
                    False,
                    None,
                    [],
                ),
            ), patch.object(
                span_review.structured,
                "run",
                return_value=('{"replacement":"invalid\\bad"}', False, None, []),
            ), patch.object(
                span_review,
                "review_one",
                return_value=([], ["Span1: overbroad outcome"]),
            ) as judge:
                self.assertFalse(span_review.review_all(Job(), "t", root, []))
                self.assertEqual(judge.call_count, 1)
                judge.return_value = ([{"draft_quote": "fake accepted"}], [])
                self.assertFalse(span_review.review_all(Job(), "t", root, []))
                self.assertEqual(judge.call_count, 1)
                (root / "paper/main.tex").write_text(
                    r"\maketitle"
                    + "\n"
                    + "A changed narrower source finding with appropriately bounded method details. "
                    + r"\cite{k}"
                )
                judge.return_value = ([], ["Span1 invalid review response"])
                self.assertFalse(span_review.review_all(Job(), "t", root, []))
                self.assertEqual(judge.call_count, 2)
            self.assertTrue(
                json.loads((root / "span-review/rejected-spans.json").read_text())
            )

    def test_unresolved_verdict_is_retained_and_resume_never_resamples(self):
        import tempfile, json, os
        from pathlib import Path
        from unittest.mock import patch

        class Job:
            def tool_start(self, *a):
                return "x"

            def tool_done(self, *a, **kw):
                pass

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "paper").mkdir()
            (root / "paper/main.tex").write_text(
                r"\maketitle"
                + "\n"
                + "A sufficiently long source finding that the reviewer cannot ground. "
                + r"\cite{k}"
            )
            source = root / "source.txt"
            source.write_text(
                "=== PAGE 1 ===\n" + "A narrow supported method is described. " * 8
            )
            rows = [{"key": "k", "status": "indexed", "text_path": str(source)}]
            unres = [
                "Span1: unresolved clause grounding: a clause is not copied exactly from the draft; supported verdict not verifiable"
            ]
            with patch.dict(
                os.environ, {"PAPERFORGE_REVIEW_NEW_ATTEMPT": ""}
            ), patch.object(span_review.db, "sources", return_value=rows), patch.object(
                span_review.opencode,
                "write_config",
                side_effect=lambda work, *a: (work / "opencode.json").write_text(
                    '{"agent":{"paperforge":{}}}'
                ),
            ), patch.object(
                span_review, "review_one", return_value=([], unres)
            ) as judge:
                self.assertFalse(span_review.review_all(Job(), "t", root, []))
                self.assertEqual(judge.call_count, 1)
                # the reviewer would now pass it; ordinary resumes must not ask again
                judge.return_value = ([{"draft_quote": "fake accepted"}], [])
                for _ in range(3):
                    self.assertFalse(span_review.review_all(Job(), "t", root, []))
                self.assertEqual(judge.call_count, 1)
                led = json.loads(
                    (root / "span-review/unresolved-spans.json").read_text()
                )
                self.assertEqual(len(led), 1)
                self.assertEqual(list(led.values())[0]["failures"], unres)
                # explicit new attempt is a distinct attempt and preserves the earlier reasons
                with patch.dict(os.environ, {"PAPERFORGE_REVIEW_NEW_ATTEMPT": "a2"}):
                    judge.return_value = (
                        [],
                        [
                            "Span1: unresolved clause grounding: no clause evidence returned"
                        ],
                    )
                    self.assertFalse(span_review.review_all(Job(), "t", root, []))
                    self.assertEqual(judge.call_count, 2)
                    self.assertFalse(span_review.review_all(Job(), "t", root, []))
                    self.assertEqual(judge.call_count, 2)
                v = list(
                    json.loads(
                        (root / "span-review/unresolved-spans.json").read_text()
                    ).values()
                )[0]
                self.assertEqual(v["history"][0]["failures"], unres)
                self.assertIn("no clause evidence", v["failures"][0])
            # changed claim text is a material change: reviewed again
            (root / "paper/main.tex").write_text(
                r"\maketitle"
                + "\n"
                + "A different sufficiently long source finding with narrower wording. "
                + r"\cite{k}"
            )
            with patch.dict(
                os.environ, {"PAPERFORGE_REVIEW_NEW_ATTEMPT": ""}
            ), patch.object(span_review.db, "sources", return_value=rows), patch.object(
                span_review.opencode,
                "write_config",
                side_effect=lambda work, *a: (work / "opencode.json").write_text(
                    '{"agent":{"paperforge":{}}}'
                ),
            ), patch.object(
                span_review, "review_one", return_value=([], unres)
            ) as j2:
                span_review.review_all(Job(), "t", root, [])
                self.assertEqual(j2.call_count, 1)

    def test_table_repair_escapes_percent(self):
        fixed = span_review.repair_table_row(
            r"Author \cite{k} & method & result \\ \hline",
            ["Author", "50% sampling", "QA evaluation"],
        )
        self.assertIn(r"50\% sampling", fixed)


class TablePromptTests(unittest.TestCase):
    def test_table_judge_defines_evaluation_as_target(self):
        import tempfile, json
        from pathlib import Path
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with patch.object(span_review, "candidates", return_value=[]), patch.object(
                span_review.opencode,
                "write_config",
                side_effect=lambda work, *a: (work / "opencode.json").write_text(
                    '{"agent":{"paperforge":{}}}'
                ),
            ), patch.object(
                span_review.structured,
                "run",
                return_value=(
                    '{"status":"unsupported","evidence_ids":[],"reason":"no evidence"}',
                    True,
                    None,
                    [],
                ),
            ) as model:
                span_review.review_one(
                    root,
                    1,
                    r"Author \cite{k} & method & evaluation target \\ \hline",
                    [],
                    [],
                )
                self.assertIn("task, dataset or benchmark", model.call_args.args[1])
                self.assertIn("under30words", model.call_args.args[1])


class TableLengthTests(unittest.TestCase):
    def test_long_model_cell_is_blocked(self):
        with self.assertRaises(ValueError):
            span_review.repair_table_row(
                "a & b & c", ["a", "long method " * 12, "QA target"]
            )


class EvaluationCoverageTests(unittest.TestCase):
    def test_table_adds_experiment_window_when_wrong_cell_has_no_task_terms(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as td:
            source = Path(td) / "source.txt"
            source.write_text(
                "=== PAGE 1 ===\n"
                + ("Speculative decoding token verification algorithm. " * 400)
                + "\n=== PAGE 2 ===\n4. Experiments\nEnglish German translation and text summarization tasks evaluated on benchmark datasets. "
                * 10
            )
            rows = [{"key": "k", "text_path": str(source)}]
            evidence = span_review.candidates(
                r"Author \cite{k} & speculative decoding & token verification \\ \hline",
                rows,
                [],
            )
            self.assertTrue(any("4. Experiments" in e["quote"] for e in evidence))
            self.assertTrue(any("algorithm." in e["quote"] for e in evidence))
            for e in evidence:
                self.assertIn(e["quote"], source.read_text())

    def test_no_cross_source_experiment_added(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as td:
            a = Path(td) / "a.txt"
            b = Path(td) / "b.txt"
            a.write_text("=== PAGE 1 ===\n" + "Source A algorithm step. " * 20)
            b.write_text(
                "=== PAGE 1 ===\n" + "4. Experiments translation evaluation. " * 20
            )
            rows = [
                {"key": "a", "text_path": str(a)},
                {"key": "b", "text_path": str(b)},
            ]
            evidence = span_review.candidates(
                r"Author \cite{a} & method & task \\ \hline", rows, []
            )
            self.assertTrue(evidence)
            self.assertTrue(all(e["source_key"] == "a" for e in evidence))


class QuoteContextTests(unittest.TestCase):
    def setUp(self):
        import tempfile
        from pathlib import Path

        self.td = tempfile.TemporaryDirectory()
        f = Path(self.td.name) / "s.txt"
        f.write_text(
            "=== PAGE 1 ===\nIntro text. " * 3
            + "=== PAGE 2 ===\nBefore context here. One limitation of speculative execution in general, is that latency is\nimproved through increased concurrency at the cost of more arithmetic operations. Thus our method helps.\n"
        )
        self.rows = [
            {"key": "k", "text_path": str(f)},
            {"key": "o", "text_path": str(f)},
        ]

    def test_quote_window_is_exact_and_contextual(self):
        block = 'The source authors state: "One limitation of speculative execution in general, is that latency is improved through increased concurrency at the cost of more arithmetic operations." \\cite{k}'
        w = span_review.quote_windows(block, self.rows, {"k"})
        self.assertEqual(len(w), 1)
        self.assertEqual(w[0]["page"], 2)
        self.assertIn("Before context here", w[0]["quote"])
        self.assertIn("Thus our method helps", w[0]["quote"])
        ev = span_review.candidates(block, self.rows, None)
        self.assertEqual(ev[0]["id"], "E1")
        self.assertEqual(ev[0]["page"], 2)
        self.assertTrue(all(e["source_key"] == "k" for e in ev))

    def test_non_quote_or_missing_quote_gets_no_window(self):
        self.assertEqual(
            span_review.quote_windows(
                "A plain claim sentence with many words in it. \\cite{k}",
                self.rows,
                {"k"},
            ),
            [],
        )
        block = 'The source authors state: "A sentence that never occurs anywhere in the source text at all." \\cite{k}'
        self.assertEqual(span_review.quote_windows(block, self.rows, {"k"}), [])
        self.assertIsNone(span_review.quoted_text("Ordinary sentence. \\cite{k}"))


class RepairCitationTests(unittest.TestCase):
    def test_repair_replacement_raw_key_becomes_page_cite_and_other_text_untouched(
        self,
    ):
        import tempfile, json
        from pathlib import Path
        from unittest.mock import patch

        class Job:
            def tool_start(self, *a):
                return "x"

            def tool_done(self, *a, **kw):
                pass

        keep = "An untouched sentence elsewhere in the paper with several plain words. \\cite{k}"
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "paper").mkdir()
            bad = "A sufficiently long source finding with a disputed broad outcome claimed. \\cite{k}"
            (root / "paper/main.tex").write_text("\\maketitle\n" + keep + "\n\n" + bad)
            source = root / "source.txt"
            source.write_text(
                "=== PAGE 1 ===\n" + "A narrow supported method is described. " * 8
            )
            rows = [{"key": "k", "status": "indexed", "text_path": str(source)}]

            def judge(root_, i, block, *a, **kw):
                return (
                    ([{"draft_quote": block}], [])
                    if block == keep
                    else ([], ["Span%d: overbroad outcome" % i])
                )

            cfg = lambda work, *a: (work / "opencode.json").write_text(
                '{"agent":{"paperforge":{}}}'
            )
            with patch.object(
                span_review.db, "sources", return_value=rows
            ), patch.object(
                span_review.opencode, "write_config", side_effect=cfg
            ), patch.object(
                span_review, "review_one", side_effect=judge
            ), patch.object(
                span_review.structured,
                "run",
                return_value=(
                    '{"replacement":"A narrow supported method is described here. [k, p.8]"}',
                    True,
                    None,
                    [],
                ),
            ), (
                patch.object(
                    span_review.evidence, "validate", return_value=[], create=True
                )
                if hasattr(span_review, "evidence")
                else patch.object(span_review.db, "sources", return_value=rows)
            ):
                span_review.review_all(Job(), "t", root, [])
            tex = (root / "paper/main.tex").read_text()
            self.assertIn("\\cite[p.~8]{k}", tex)
            self.assertNotIn("[k, p.8]", tex)
            self.assertTrue(tex.startswith("\\maketitle\n" + keep))
            self.assertEqual(
                tex.count("{k}"), 2
            )  # kept sentence + one repaired cite, no duplicate
            self.assertNotIn("\\cite{k} \\cite", tex)


class RepairGroundingTests(unittest.TestCase):
    SRC = [
        "Chinchilla 70B draft with K=4 reached 2.01x on XSum. T5-XXL translation was evaluated."
    ]

    def test_invented_name_or_number_is_ungrounded(self):
        self.assertEqual(
            span_review.ungrounded_terms(
                "Speculative sampling with a Chimera draft reaches 3.5x on XSum.",
                self.SRC,
            )[:2],
            ["Chimera", "3.5x"],
        )

    def test_names_and_numbers_from_source_are_grounded(self):
        self.assertEqual(
            span_review.ungrounded_terms(
                "A Chinchilla 70B draft with K=4 reaches 2.01x on XSum. \\cite{k}",
                self.SRC,
            ),
            [],
        )

    def test_repair_with_invented_name_is_not_written(self):
        import tempfile
        from pathlib import Path
        from unittest.mock import patch

        class Job:
            def tool_start(self, *a):
                return "x"

            def tool_done(self, *a, **kw):
                pass

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "paper").mkdir()
            bad = "A sufficiently long source finding with a disputed broad outcome claimed. \\cite{k}"
            (root / "paper/main.tex").write_text("\\maketitle\n" + bad)
            source = root / "s.txt"
            source.write_text(
                "=== PAGE 1 ===\n" + "A narrow supported method is described. " * 8
            )
            rows = [{"key": "k", "status": "indexed", "text_path": str(source)}]
            cfg = lambda work, *a: (work / "opencode.json").write_text(
                '{"agent":{"paperforge":{}}}'
            )
            with patch.object(
                span_review.db, "sources", return_value=rows
            ), patch.object(
                span_review.opencode, "write_config", side_effect=cfg
            ), patch.object(
                span_review, "review_one", return_value=([], ["Span1: x"])
            ), patch.object(
                span_review.structured,
                "run",
                return_value=(
                    '{"replacement":"A narrow method is described with a Chimera model. [k, p.1]"}',
                    True,
                    None,
                    [],
                ),
            ):
                span_review.review_all(Job(), "t", root, [])
            self.assertEqual(
                (root / "paper/main.tex").read_text(), "\\maketitle\n" + bad
            )


class EvidenceSelectionTests(unittest.TestCase):
    def src(self, text):
        import tempfile
        from pathlib import Path

        self.td = tempfile.TemporaryDirectory()
        f = Path(self.td.name) / "s.txt"
        f.write_text(text)
        return [{"key": "k", "text_path": str(f)}]

    def test_windows_are_distinct_regions(self):
        rows = self.src(
            "=== PAGE 1 ===\n"
            + "".join(
                f"Item {i} speculative sampling draft model accelerates decoding. "
                for i in range(60)
            )
        )
        ev = span_review.candidates(
            "Speculative sampling draft model accelerates decoding in this work. \\cite{k}",
            rows,
            [],
            limit=4,
        )
        self.assertGreaterEqual(len(ev), 2)
        quotes = [e["quote"] for e in ev]
        self.assertEqual(len(set(quotes)), len(quotes))
        text = open(rows[0]["text_path"]).read()
        starts = sorted(text.index(q) for q in quotes)
        self.assertTrue(all(b - a >= 1000 for a, b in zip(starts, starts[1:])))

    def test_rare_claim_term_outranks_common_terms(self):
        common = "decoding model draft sampling speedup " * 40
        rare = "In the Chinchilla variant with frozen backbone the result holds. "
        rows = self.src(
            "=== PAGE 1 ===\n"
            + common
            + "\n=== PAGE 2 ===\n"
            + common
            + "\n=== PAGE 3 ===\n"
            + rare
            + common[:300]
        )
        ev = span_review.candidates(
            "The Chinchilla frozen variant gives decoding model speedup. \\cite{k}",
            rows,
            [],
            limit=1,
        )
        self.assertEqual(ev[0]["page"], 3)

    def test_insufficient_evidence_retries_wider_then_stays_unresolved_without_rewrite(
        self,
    ):
        import tempfile, json
        from pathlib import Path
        from unittest.mock import patch

        class Job:
            def tool_start(self, *a):
                return "x"

            def tool_done(self, *a, **kw):
                pass

        limits = []
        real = span_review.candidates

        def spy(block, sources, packet, limit=4):
            limits.append(limit)
            return real(block, sources, packet, limit)

        body = '{"status":"insufficient_evidence","evidence_ids":[],"reason":"experiments not in excerpts"}'
        reply = (body, True, None, [{"kind": "text", "text": body}])
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "paper").mkdir()
            tex = "\\maketitle\nA sufficiently long claim about experimental results on a task. \\cite{k}"
            (root / "paper/main.tex").write_text(tex)
            source = root / "s.txt"
            source.write_text(
                "=== PAGE 1 ===\n" + "A narrow supported method is described. " * 80
            )
            rows = [{"key": "k", "status": "indexed", "text_path": str(source)}]
            cfg = lambda work, *a: (work / "opencode.json").write_text(
                '{"agent":{"paperforge":{}}}'
            )
            with patch.object(
                span_review.db, "sources", return_value=rows
            ), patch.object(
                span_review.opencode, "write_config", side_effect=cfg
            ), patch.object(
                span_review, "candidates", side_effect=spy
            ), patch.object(
                span_review.structured, "run", return_value=reply
            ) as run, patch.object(
                span_review.opencode, "run_text"
            ) as rewrite:
                ok = span_review.review_all(Job(), "t", root, [])
            self.assertFalse(ok)
            self.assertIn(4, limits)
            self.assertIn(8, limits)
            self.assertEqual((root / "paper/main.tex").read_text(), tex)
            rewrite.assert_not_called()
            self.assertEqual(run.call_count, 2)
            self.assertFalse((root / "span-review/rejected-spans.json").exists())
            fb = json.loads((root / "review-feedback.json").read_text())["errors"]
            self.assertTrue(any("insufficient evidence" in e for e in fb))


class QuoteDedupeTests(unittest.TestCase):
    def test_other_windows_do_not_overlap_quote_window(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "s.txt"
            f.write_text(
                "=== PAGE 1 ===\n"
                + "".join(
                    f"Item {i} speculative sampling draft model accelerates decoding. "
                    for i in range(10)
                )
                + "One limitation of speculative execution in general is increased arithmetic operations here. "
                + "".join(
                    f"Later {i} speculative sampling draft model accelerates decoding. "
                    for i in range(60)
                )
            )
            rows = [{"key": "k", "text_path": str(f)}]
            block = 'The source authors state: "One limitation of speculative execution in general is increased arithmetic operations here." \\cite{k}'
            ev = span_review.candidates(block, rows, [])
            text = f.read_text().split("\n", 1)[1]
            starts = sorted(
                text.index(e["quote"][:60]) if e["quote"][:60] in text else 0
                for e in ev
            )
            self.assertEqual(ev[0]["id"], "E1")
            self.assertIn("One limitation", ev[0]["quote"])
            self.assertTrue(
                all(b - a >= 1000 for a, b in zip(starts, starts[1:])), starts
            )


class QuoteBoundaryTests(unittest.TestCase):
    PAGE = "=== PAGE 1 ===\nIntro words here. Previous sentence about other things. One limitation of speculative execution in general is that latency is improved through increased concurrency at the cost of more arithmetic operations. Next sentence follows.\n"
    BLOCK = 'The source authors state: "One limitation of speculative execution in general is that latency is improved through increased concurrency at the cost of more arithmetic operations." \\cite{k}'

    def go(self, block, page, replies):
        import tempfile, json
        from pathlib import Path
        from unittest.mock import patch

        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        (root / "paper").mkdir()
        f = root / "s.txt"
        f.write_text(page)
        rows = [{"key": "k", "status": "indexed", "text_path": str(f)}]
        cfg = lambda work, *a: (work / "opencode.json").write_text(
            '{"agent":{"paperforge":{}}}'
        )

        def reply(d):
            b = json.dumps(d)
            return (b, True, None, [{"kind": "text", "text": b}])

        with patch.object(
            span_review.opencode, "write_config", side_effect=cfg
        ), patch.object(
            span_review.structured, "run", side_effect=[reply(x) for x in replies]
        ) as run:
            out = span_review.review_one(root, 1, block, rows, [])
        self.prompts = [c.args[1] for c in run.call_args_list]
        return out, run.call_count

    REJ = {
        "status": "unsupported",
        "evidence_ids": ["E1"],
        "reason": "reviewer says no",
    }

    def adj(
        self,
        phrase="Previous sentence about other things",
        own=True,
        neg=False,
        other=False,
    ):
        return {
            "own_statement": own,
            "negated_or_conditioned": neg,
            "attributed_to_other_work": other,
            "context_phrase": phrase,
        }

    def test_absent_quote_never_reaches_model(self):
        b = self.BLOCK.replace("arithmetic operations.", "invented operations.")
        (ent, fail), calls = self.go(b, self.PAGE, [])
        self.assertEqual((ent, calls), ([], 0))
        self.assertIn("unresolved quote provenance", fail[0])

    def test_mid_sentence_fragment_is_not_complete(self):
        page = self.PAGE.replace(
            "Previous sentence about other things. ", "Previous sentence mentions that "
        ).replace("One limitation", "one limitation")
        b = self.BLOCK.replace("One limitation", "one limitation")
        (ent, fail), calls = self.go(b, page, [])
        self.assertEqual(calls, 0)
        self.assertIn("unresolved quote provenance", fail[0])

    def test_reviewer_rejects_adjudicator_affirms_stays_unresolved_with_both_reasons(
        self,
    ):
        (ent, fail), calls = self.go(self.BLOCK, self.PAGE, [self.REJ, self.adj()])
        self.assertEqual((ent, calls), ([], 2))
        self.assertIn("unresolved quote judgment", fail[0])
        self.assertIn("reviewer says no", fail[0])
        self.assertIn("affirmed", fail[0])

    def test_negating_context_is_rejected_by_adjudicator_and_stays_unresolved(self):
        page = self.PAGE.replace(
            "One limitation", "It is not the case that one limitation"
        ).replace("Previous sentence about other things.", "Previous sentence.")
        # quote starts mid-sentence in this page, so provenance (not the model) blocks it
        b = self.BLOCK
        (ent, fail), calls = self.go(
            b,
            page.replace(
                "It is not the case that one limitation", "Smith argue: One limitation"
            ),
            [self.REJ, self.adj(phrase="Smith argue", own=False, other=True)],
        )
        self.assertEqual(ent, [])
        self.assertIn("rejected", fail[0])

    def test_ungrounded_context_phrase_is_unchecked_not_affirmed(self):
        (ent, fail), calls = self.go(
            self.BLOCK,
            self.PAGE,
            [self.REJ, self.adj(phrase="text that is nowhere in the passage")],
        )
        self.assertEqual(ent, [])
        self.assertIn("unchecked", fail[0])

    def test_reviewer_support_passes_without_adjudication(self):
        q = "One limitation of speculative execution in general is that latency is improved through increased concurrency at the cost of more arithmetic operations."
        ok = {
            "status": "supported",
            "evidence_ids": ["E1"],
            "reason": "quote and context agree",
            "clauses": [
                {
                    "clause": 'The source authors state: "' + q + '"',
                    "evidence_id": "E1",
                    "excerpt": q,
                }
            ],
        }
        (ent, fail), calls = self.go(self.BLOCK, self.PAGE, [ok])
        self.assertEqual((fail, calls), ([], 1))
        self.assertTrue(ent)

    def test_supported_without_verifiable_clause_evidence_is_unresolved(self):
        q = "One limitation of speculative execution in general is that latency is improved through increased concurrency at the cost of more arithmetic operations."

        def mk(clauses):
            return (
                {
                    "status": "supported",
                    "evidence_ids": ["E1"],
                    "reason": "x",
                    "clauses": clauses,
                }
                if clauses is not None
                else {"status": "supported", "evidence_ids": ["E1"], "reason": "x"}
            )

        good = {
            "clause": 'The source authors state: "' + q + '"',
            "evidence_id": "E1",
            "excerpt": q,
        }
        for bad, word in (
            (None, "no clause"),
            (
                [
                    dict(
                        good,
                        excerpt="Speedups are bounded by approximation quality of the draft model.",
                    )
                ],
                "excerpt",
            ),
            ([dict(good, clause="The source authors state")], "cover"),
            (
                [dict(good, clause="an invented clause not in the draft")],
                "clause is not copied",
            ),
        ):
            (ent, fail), _ = self.go(self.BLOCK, self.PAGE, [mk(bad), mk(bad)])
            self.assertEqual(ent, [])
            self.assertIn("unresolved clause grounding", fail[0])
            self.assertIn(word, fail[0])

    def test_phrase_taken_from_inside_the_quote_is_not_grounding(self):
        (ent, fail), calls = self.go(
            self.BLOCK,
            self.PAGE,
            [
                self.REJ,
                self.adj(
                    phrase="at the cost of more arithmetic operations",
                    own=False,
                    neg=True,
                ),
            ],
        )
        self.assertEqual(ent, [])
        self.assertIn("unchecked", fail[0])

    def test_adjudicator_never_sees_quote_text_only_marker(self):
        self.go(self.BLOCK, self.PAGE, [self.REJ, self.adj()])
        p = [x for x in self.prompts if "QUOTED SENTENCE" in x]
        self.assertTrue(p)
        passage = p[0].split("PASSAGE (quoted sentence replaced by the marker):")[1]
        self.assertIn("[QUOTED SENTENCE]", passage)
        self.assertNotIn("arithmetic operations", passage)

    def test_phrase_from_surrounding_text_is_grounding(self):
        (ent, fail), calls = self.go(
            self.BLOCK,
            self.PAGE,
            [self.REJ, self.adj(phrase="Previous sentence about other things")],
        )
        self.assertIn("affirmed", fail[0])


class ClauseGroundingMathTests(unittest.TestCase):
    def test_unicode_math_letters_in_evidence_match_plain_excerpt(self):
        ev = [
            {
                "id": "E1",
                "quote": "Generating a draft of length \U0001d43e. Then verify.",
            }
        ]
        cl = [
            {
                "clause": "A draft of length K is generated",
                "evidence_id": "E1",
                "excerpt": "draft of length K.",
            }
        ]
        self.assertIsNone(
            span_review.clause_grounding_gap("A draft of length K is generated", cl, ev)
        )


class QuoteNormalisationTests(unittest.TestCase):
    def src(self, body):
        import tempfile
        from pathlib import Path

        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        f = Path(self.td.name) / "s.txt"
        f.write_text(
            "=== PAGE 7 ===\nFigure 1. Previous. Note that as \U0001d43e\nincreases, the overall speedup plateaus or even regresses, with XSum being optimal at \U0001d43e = 3. The variance rises.\n"
        )
        return [{"key": "k", "text_path": str(f)}]

    def block(self, q):
        return 'The source authors state: "' + q + '" \\cite{k}'

    GOOD = "Note that as \\ensuremath{\\mathit{K}}\nincreases, the overall speedup plateaus or even regresses, with XSum being optimal at \\ensuremath{\\mathit{K}} = 3."

    def test_tex_math_quote_matches_unicode_math_source(self):
        r = span_review.verify_quote(self.block(self.GOOD), self.src(""), {"k"})
        self.assertTrue(r["complete"])
        self.assertEqual(r["page"], 7)
        self.assertTrue(
            span_review.quote_windows(self.block(self.GOOD), self.src(""), {"k"})
        )

    def test_changed_letter_or_number_does_not_match(self):
        rows = self.src("")
        for bad in (
            self.GOOD.replace("= 3", "= 4"),
            self.GOOD.replace("{K}", "{L}", 1),
            self.GOOD.replace("plateaus or even regresses", "plateaus"),
        ):
            self.assertEqual(
                span_review.verify_quote(self.block(bad), rows, {"k"}),
                {"present": False},
            )

    def test_meaning_bearing_markup_is_not_stripped(self):
        rows = self.src("")
        self.assertEqual(
            span_review.verify_quote(
                self.block(self.GOOD.replace("overall", "\\emph{overall}")), rows, {"k"}
            ),
            {"present": False},
        )
        self.assertEqual(
            span_review.tex_plain(r"50\% of \textbf{x}"), r"50% of \textbf{x}"
        )

    def test_plain_source_only_maps_math_letters(self):
        self.assertEqual(
            span_review.plain_source("\U0001d43e = 3 \u00e9"), "K = 3 \u00e9"
        )


class QuestionPremiseTests(unittest.TestCase):
    def test_entity_absent_from_every_source_is_reported_not_substituted(self):
        from app import answering

        src = [
            "Medusa speeds up Vicuna-7B and Vicuna-13B models. Medusa-1 freezes the backbone. T5-XXL is also used."
        ]
        self.assertEqual(
            answering.missing_entities(
                "/ask What speedup does the Medusa paper report for GPT-4?", src
            ),
            ["GPT-4"],
        )
        self.assertEqual(
            answering.missing_entities("How does Medusa-1 differ on Vicuna-7B?", src),
            [],
        )
        self.assertEqual(
            answering.missing_entities("Is gpt 4 used?", src), []
        )  # no named entity pattern, no premise claim
        self.assertEqual(
            answering.missing_entities("What about T5-XXL and Medusa-3?", src),
            ["Medusa-3"],
        )

    def test_punctuation_case_and_math_letters_do_not_cause_false_absence(self):
        from app import answering

        self.assertEqual(
            answering.missing_entities(
                "Does K-3 matter? What about LLaMA-2?",
                ["value of \U0001d43e-3 and llama 2 results"],
            ),
            [],
        )
