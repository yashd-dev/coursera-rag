import unittest
from app.structured import validate


class SchemaTests(unittest.TestCase):
    def test_strict_enum_required_and_unknown_fields(self):
        s = {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["supported", "unavailable"]},
                "id": {"type": "string"},
            },
            "required": ["status", "id"],
            "additionalProperties": False,
        }
        validate({"status": "supported", "id": "E1"}, s)
        for value in [
            {"status": "available", "id": "E1"},
            {"status": "supported"},
            {"status": "supported", "id": "E1", "extra": "x"},
            "status: supported",
        ]:
            with self.assertRaises(ValueError):
                validate(value, s)


class ArrayValidationTests(unittest.TestCase):
    def setUp(self):
        global structured
        from app import structured

    def test_unknown_evidence_id_or_scalar_blocked(self):
        schema = {
            "type": "array",
            "items": {"type": "string", "enum": ["E1", "E2"]},
            "maxItems": 2,
        }
        structured.validate(["E1"], schema)
        for bad in ("E1", ["E3"], [None], ["E1", "E1", "E2"]):
            with self.assertRaises(ValueError):
                structured.validate(bad, schema)
