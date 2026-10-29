import inspect
import unittest

from app import span_review


class ExcerptLimitPrompt(unittest.TestCase):
    def test_prompt_keeps_excerpt_under_schema_limit(self):
        src = inspect.getsource(span_review)
        # A live probe returned a 521-character excerpt and the provider rejected it against the 400 schema limit.
        self.assertIn("limited to 350 characters", src)
        self.assertIn('"excerpt": {"type": "string", "maxLength": 400}', src)
        self.assertIn("do not join pieces", src)


if __name__ == "__main__":
    unittest.main()
