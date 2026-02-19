"""Unit tests for regex rules."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from version_guard.exceptions import FileChangedException
from version_guard.rules.regex_rule import RegexRule


class RegexRuleTests(unittest.TestCase):
    """Tests for RegexRule behavior."""

    def test_parse_file_updates_version_and_raises(self) -> None:
        """Rule should rewrite the file when version differs."""
        with TemporaryDirectory() as tempdir:
            path = Path(tempdir) / "pyproject.toml"
            path.write_text('python = "3.10"\n', encoding="utf-8")

            rule = RegexRule(
                name="python",
                file_glob="*.toml",
                pattern=r'python = "(?P<version>\d+\.\d+)"',
                version="3.11",
            )

            with self.assertRaises(FileChangedException):
                rule.parse_file(path)

            self.assertEqual(
                path.read_text(encoding="utf-8"),
                'python = "3.11"\n',
            )

    def test_parse_file_no_change(self) -> None:
        """Rule should not modify file if version is already correct."""
        with TemporaryDirectory() as tempdir:
            path = Path(tempdir) / "pyproject.toml"
            path.write_text('python = "3.11"\n', encoding="utf-8")

            rule = RegexRule(
                name="python",
                file_glob="*.toml",
                pattern=r'python = "(?P<version>\d+\.\d+)"',
                version="3.11",
            )

            rule.parse_file(path)
            self.assertEqual(path.read_text(encoding="utf-8"), 'python = "3.11"\n')

    def test_parse_file_skips_non_matching_glob(self) -> None:
        """Files not matching the configured glob should be ignored."""
        with TemporaryDirectory() as tempdir:
            path = Path(tempdir) / "pyproject.toml"
            path.write_text('python = "3.10"\n', encoding="utf-8")

            rule = RegexRule(
                name="python",
                file_glob="*.yaml",
                pattern=r'python = "(?P<version>\d+\.\d+)"',
                version="3.11",
            )

            rule.parse_file(path)
            self.assertEqual(path.read_text(encoding="utf-8"), 'python = "3.10"\n')


if __name__ == "__main__":
    unittest.main()
