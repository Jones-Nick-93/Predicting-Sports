"""Static contracts for the sanitized, read-only SQL template."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
SQL = (ROOT / "schema_discovery.sql").read_text(encoding="utf-8")
PROJECT_TEXT = "\n".join(
    path.read_text(encoding="utf-8", errors="ignore")
    for path in ROOT.rglob("*")
    if path.is_file()
    and not {".git", "__pycache__", ".pytest_cache"}.intersection(path.parts)
    and path.suffix not in {".pyc", ".zip"}
)


class PublicSafetyTests(unittest.TestCase):
    def test_environment_fingerprints_are_absent(self):
        forbidden_patterns = {
            "local user path": r"[A-Z]:\\Users\\[^\\\s]+",
            "UNC path": r"\\\\[^\\\s]+\\[^\\\s]+",
            "email address": r"\b[\w.+-]+@[\w.-]+\.[A-Z]{2,}\b",
            "IPv4 address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
            "credential assignment": (
                r"\b(?:password|passwd|pwd|api[_-]?key|secret|token)\b\s*[:=]"
            ),
        }
        for label, pattern in forbidden_patterns.items():
            with self.subTest(label=label):
                self.assertIsNone(re.search(pattern, PROJECT_TEXT, re.IGNORECASE))

    def test_templates_retain_fictional_placeholders(self):
        for value in ("YOUR_SCHEMA", "YOUR_TABLE", "YOUR_KNOWN_VALUE", "STATUS_FLAG_A"):
            with self.subTest(value=value):
                self.assertIn(value, SQL)

    def test_no_write_or_permission_statements_exist(self):
        write_pattern = re.compile(
            r"^\s*(INSERT|UPDATE|DELETE|MERGE|DROP|ALTER|TRUNCATE|CREATE|"
            r"GRANT|REVOKE|DENY|BACKUP|RESTORE)\b",
            flags=re.IGNORECASE | re.MULTILINE,
        )
        self.assertEqual(write_pattern.findall(SQL), [])

    def test_dynamic_identifiers_are_quoted(self):
        self.assertGreaterEqual(SQL.count("QUOTENAME("), 20)

    def test_searched_values_are_parameterized(self):
        self.assertIn("@value NVARCHAR(100)", SQL)
        self.assertIn("@sentinel DATE", SQL)
        self.assertIn("@sample_size INT", SQL)


if __name__ == "__main__":
    unittest.main()
