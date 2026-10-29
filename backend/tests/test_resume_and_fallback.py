import unittest
from app import pipeline


class ImplicitResumeTests(unittest.TestCase):
    def r(self, text, phase="discovery_paused"):
        return pipeline.route(text, {"phase": phase})[0]

    def test_continue_phrases_resume_paused_runs(self):
        for text in (
            "continue please",
            "Continue",
            "go ahead",
            "its ok if its ambiguiius continue and make me a new paper irrepective",
        ):
            self.assertEqual(self.r(text), "resume", text)

    def test_questions_stop_and_slash_commands_are_not_resume(self):
        for text in (
            "Can we continue?",
            "what does the paper say, continue",
            "stop, don't continue",
            "cancel this and start a new topic",
            "/ask continue",
            "/edit continue the conclusion",
            "Rewrite the conclusion",
        ):
            self.assertNotEqual(self.r(text), "resume", text)

    def test_only_paused_phases_resume(self):
        for phase in ("done", "ready", "editing", "new"):
            self.assertNotEqual(self.r("continue please", phase), "resume", phase)

    def test_explicit_resume_unchanged(self):
        self.assertEqual(self.r("/resume", "reading_paused"), "resume")


class FallbackQueryTests(unittest.TestCase):
    def test_management_request_drops_filler_without_inventing_scope(self):
        p = pipeline.fallback_plan(
            "just help me find papers on management and what is the latest trend"
        )
        self.assertTrue(p["fallback"])
        self.assertEqual(p["queries"][0], "management")
        joined = " ".join(p["queries"]).lower()
        for bad in ("help", "find", "what", "strategic"):
            self.assertNotIn(bad, joined)

    def test_technical_topics_keep_their_terms(self):
        self.assertEqual(
            pipeline.fallback_plan("Literature review on speculative decoding for LLM acceleration")["queries"][0],
            "speculative decoding LLM acceleration",
        )
        self.assertEqual(pipeline.fallback_plan("review graph RAG")["queries"][0], "graph RAG")


if __name__ == "__main__":
    unittest.main()
