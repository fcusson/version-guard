"""Unit tests for the base Rule class."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from version_guard.rules.base import Rule


class DummyRule(Rule):
    """Concrete rule implementation for base class tests."""

    def parse_file(self, path: Path) -> None:
        """No-op parse implementation for tests."""


class BaseRuleTests(unittest.TestCase):
    """Tests for shared Rule behavior."""

    def test_invalid_version(self) -> None:
        """Version comparison should ignore surrounding whitespace."""
        rule = DummyRule("name", "*.txt", "1.2.3")

        self.assertFalse(rule.invalid_version(" 1.2.3 "))
        self.assertTrue(rule.invalid_version("1.2.4"))
        self.assertTrue(rule.invalid_version(None))

    def test_find_all(self) -> None:
        """Glob search should return matching files."""
        with TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            match = root / "a.txt"
            other = root / "b.md"
            match.write_text("a", encoding="utf-8")
            other.write_text("b", encoding="utf-8")

            rule = DummyRule("name", "*.txt", "1")
            found = rule.find_all(root)

        self.assertEqual(found, [match])

    def test_git_add_invokes_git(self) -> None:
        """git_add should call git add for the provided file."""
        with patch("version_guard.rules.base.subprocess.run") as run_mock:
            Rule.git_add(Path("README.md"))

        run_mock.assert_called_once_with(
            ["git", "add", "README.md"],
            check=False,
        )


if __name__ == "__main__":
    unittest.main()
