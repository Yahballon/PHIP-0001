import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from validate_registry import load_registry, validate_entry

GOOD = {
    "schema_version": "1.0",
    "title_id": "PPSA12345",
    "app_id": "io.github.exampledev.example-app",
    "name": "Example App",
    "developer": "Example Developer",
    "owner": "exampledev",
    "source_repo": "https://github.com/exampledev/example-app",
    "status": "reserved",
    "created": "2026-10-13"
}

class ValidationTests(unittest.TestCase):
    def test_example_is_valid(self):
        self.assertEqual(validate_entry(GOOD, "PPSA12345.json"), [])

    def test_title_filename_must_match(self):
        self.assertTrue(validate_entry(GOOD, "PPSA54321.json"))

    def test_placeholder_id_rejected(self):
        data = dict(GOOD, title_id="PPSA99999")
        self.assertTrue(validate_entry(data, "PPSA99999.json"))

    def test_other_owner_namespace_rejected(self):
        data = dict(GOOD, app_id="io.github.someoneelse.test")
        self.assertTrue(validate_entry(data, "PPSA12345.json"))

    def test_bad_url_rejected(self):
        data = dict(GOOD, source_repo="https://example.com/repo")
        self.assertTrue(validate_entry(data, "PPSA12345.json"))

    def test_duplicate_app_id_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "PPSA12345.json").write_text(json.dumps(GOOD), encoding="utf-8")
            data = dict(GOOD, title_id="PPSA12346")
            (p / "PPSA12346.json").write_text(json.dumps(data), encoding="utf-8")
            _, errors = load_registry(p)
            self.assertTrue(any("duplicate app_id" in error for error in errors))

    def test_existing_registration_is_valid(self):
        directory = Path(__file__).resolve().parents[1] / "registry"
        _, errors = load_registry(directory)
        self.assertEqual(errors, [])

if __name__ == "__main__":
    unittest.main()
