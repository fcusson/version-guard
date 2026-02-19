"""Unit tests for XML rules."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from version_guard.exceptions import FileChangedException, ParsingException
from version_guard.rules.xml_rule import XmlRule


class XmlRuleTests(unittest.TestCase):
    """Tests for XmlRule behavior."""

    def test_repr_contains_core_fields(self) -> None:
        """Rule repr should include glob, package, and version."""
        rule = XmlRule(
            name="sdk",
            file_glob="*.xml",
            package="A",
            version="3.0.0",
        )

        text = repr(rule)

        self.assertIn("*.xml", text)
        self.assertIn("A", text)
        self.assertIn("3.0.0", text)

    def test_parse_file_updates_matching_package(self) -> None:
        """Rule should update version for matching package node."""
        content = (
            "<Project>"
            '<Sdk Name="A" Version="1.0.0" />'
            '<Sdk Name="B" Version="2.0.0" />'
            "</Project>"
        )

        with TemporaryDirectory() as tempdir:
            path = Path(tempdir) / "project.xml"
            path.write_text(content, encoding="utf-8")

            rule = XmlRule(
                name="sdk",
                file_glob="*.xml",
                package="A",
                version="3.0.0",
            )

            with self.assertRaises(FileChangedException):
                rule.parse_file(path)

            modified = path.read_text(encoding="utf-8")
            self.assertIn('Name="A" Version="3.0.0"', modified)
            self.assertIn('Name="B" Version="2.0.0"', modified)

    def test_parse_file_no_change(self) -> None:
        """Rule should not change file when version already matches."""
        content = '<Project><Sdk Name="A" Version="3.0.0" /></Project>'

        with TemporaryDirectory() as tempdir:
            path = Path(tempdir) / "project.xml"
            path.write_text(content, encoding="utf-8")

            rule = XmlRule(
                name="sdk",
                file_glob="*.xml",
                package="A",
                version="3.0.0",
            )

            rule.parse_file(path)
            self.assertIn('Name="A" Version="3.0.0"', path.read_text(encoding="utf-8"))

    def test_parse_file_skips_non_matching_glob(self) -> None:
        """Rule should skip files that do not match the configured glob."""
        content = '<Project><Sdk Name="A" Version="1.0.0" /></Project>'

        with TemporaryDirectory() as tempdir:
            path = Path(tempdir) / "project.xml"
            path.write_text(content, encoding="utf-8")

            rule = XmlRule(
                name="sdk",
                file_glob="*.csproj",
                package="A",
                version="3.0.0",
            )

            rule.parse_file(path)
            self.assertIn('Name="A" Version="1.0.0"', path.read_text(encoding="utf-8"))

    def test_parse_file_raises_when_root_is_missing(self) -> None:
        """Rule should raise ParsingException when XML root is missing."""
        with TemporaryDirectory() as tempdir:
            path = Path(tempdir) / "project.xml"
            path.write_text("<Project />", encoding="utf-8")

            rule = XmlRule(
                name="sdk",
                file_glob="*.xml",
                package="A",
                version="3.0.0",
            )

            with patch(
                "version_guard.rules.xml_rule.ElementTree.getroot",
                return_value=None,
            ):
                with self.assertRaises(ParsingException):
                    rule.parse_file(path)


if __name__ == "__main__":
    unittest.main()
