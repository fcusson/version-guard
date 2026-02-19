"""Unit tests for the execution engine."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from version_guard.engine import (
    _apply_regex_rules,
    _apply_xml_rules,
    build_execution_plan,
    discover_files_once,
    execute_plan,
)
from version_guard.exceptions import ParsingException
from version_guard.rules.regex_rule import RegexRule
from version_guard.rules.xml_rule import XmlRule


class EngineTests(unittest.TestCase):
    """Behavior tests for the execution engine."""

    def test_discover_files_once_matches_union_of_globs(self) -> None:
        """The discovery pass should return files matching any configured glob."""
        with TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            (root / "a.txt").write_text("a", encoding="utf-8")
            (root / "b.xml").write_text("<root />", encoding="utf-8")
            (root / "c.md").write_text("c", encoding="utf-8")

            files = discover_files_once(root, {"*.txt", "*.xml"})

            names = sorted(path.name for path in files)
            self.assertEqual(names, ["a.txt", "b.xml"])

    def test_discover_files_once_skips_directories(self) -> None:
        """Directory entries should not be returned by discovery."""
        with TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            (root / "nested").mkdir()
            (root / "nested" / "file.txt").write_text("x", encoding="utf-8")

            files = discover_files_once(root, {"*"})

            self.assertEqual(files, [root / "nested" / "file.txt"])

    def test_build_execution_plan_ignores_non_matching_files(self) -> None:
        """Plan should include only files with at least one matching rule."""
        with TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            a = root / "a.ini"
            b = root / "b.txt"
            a.write_text("python=3.10\n", encoding="utf-8")
            b.write_text("hello\n", encoding="utf-8")

            rule = RegexRule(
                name="python",
                file_glob="*.ini",
                pattern=r"python=(?P<version>\d+\.\d+)",
                version="3.11",
            )

            plan = build_execution_plan([a, b], [rule])

            self.assertEqual(plan, {a: [rule]})

    def test_apply_regex_rules_no_change_returns_false(self) -> None:
        """Regex helper should return False when content is already compliant."""
        with TemporaryDirectory() as tempdir:
            path = Path(tempdir) / "config.ini"
            path.write_text("python=3.11\n", encoding="utf-8")

            rule = RegexRule(
                name="python",
                file_glob="*.ini",
                pattern=r"python=(?P<version>\d+\.\d+)",
                version="3.11",
            )

            changed = _apply_regex_rules(path, [rule])

            self.assertFalse(changed)

    def test_apply_xml_rules_updates_version(self) -> None:
        """XML helper should update matching nodes and return True."""
        with TemporaryDirectory() as tempdir:
            path = Path(tempdir) / "project.xml"
            path.write_text(
                '<Project><Sdk Name="A" Version="1.0.0" /></Project>',
                encoding="utf-8",
            )

            rule = XmlRule(
                name="sdk",
                file_glob="*.xml",
                package="A",
                version="3.0.0",
            )

            changed = _apply_xml_rules(path, [rule])

            self.assertTrue(changed)
            self.assertIn('Version="3.0.0"', path.read_text(encoding="utf-8"))

    def test_apply_xml_rules_no_change_returns_false(self) -> None:
        """XML helper should return False when no updates are needed."""
        with TemporaryDirectory() as tempdir:
            path = Path(tempdir) / "project.xml"
            path.write_text(
                '<Project><Sdk Name="A" Version="3.0.0" /></Project>',
                encoding="utf-8",
            )

            rule = XmlRule(
                name="sdk",
                file_glob="*.xml",
                package="A",
                version="3.0.0",
            )

            changed = _apply_xml_rules(path, [rule])

            self.assertFalse(changed)

    def test_apply_xml_rules_handles_missing_version_attr(self) -> None:
        """XML helper should treat missing version as invalid and set target."""
        with TemporaryDirectory() as tempdir:
            path = Path(tempdir) / "project.xml"
            path.write_text(
                '<Project><Sdk Name="A" /></Project>',
                encoding="utf-8",
            )

            rule = XmlRule(
                name="sdk",
                file_glob="*.xml",
                package="A",
                version="3.0.0",
            )

            changed = _apply_xml_rules(path, [rule])

            self.assertTrue(changed)
            self.assertIn('Version="3.0.0"', path.read_text(encoding="utf-8"))

    def test_apply_xml_rules_ignores_non_element_nodes(self) -> None:
        """XML helper should ignore non-Element values from iterators."""
        with TemporaryDirectory() as tempdir:
            path = Path(tempdir) / "project.xml"
            path.write_text(
                '<Project><Sdk Name="A" Version="1.0.0" /></Project>',
                encoding="utf-8",
            )

            rule = XmlRule(
                name="sdk",
                file_glob="*.xml",
                package="A",
                version="3.0.0",
            )
            rule.get_version_nodes = lambda _root: iter([None])  # type: ignore[method-assign]

            changed = _apply_xml_rules(path, [rule])

            self.assertFalse(changed)

    def test_apply_xml_rules_raises_when_root_is_missing(self) -> None:
        """XML helper should raise when parsed tree has no root element."""
        with TemporaryDirectory() as tempdir:
            path = Path(tempdir) / "project.xml"
            path.write_text("<Project />", encoding="utf-8")

            rule = XmlRule(
                name="sdk",
                file_glob="*.xml",
                package="A",
                version="3.0.0",
            )

            with patch("version_guard.engine.ElementTree.getroot", return_value=None):
                with self.assertRaises(ParsingException):
                    _apply_xml_rules(path, [rule])

    def test_execute_plan_applies_multiple_rules_with_single_write(self) -> None:
        """A file should be transformed by all matching regex rules."""
        with TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            file_path = root / "config.ini"
            file_path.write_text(
                "python=3.10\npackage=1.0.0\n",
                encoding="utf-8",
            )

            python_rule = RegexRule(
                name="python",
                file_glob="*.ini",
                pattern=r"python=(?P<version>\d+\.\d+)",
                version="3.11",
            )
            package_rule = RegexRule(
                name="package",
                file_glob="*.ini",
                pattern=r"package=(?P<version>\d+\.\d+\.\d+)",
                version="2.0.0",
            )

            plan = build_execution_plan(
                [file_path], [python_rule, package_rule])
            modified = execute_plan(plan)

            self.assertEqual(modified, [file_path])
            self.assertEqual(
                file_path.read_text(encoding="utf-8"),
                "python=3.11\npackage=2.0.0\n",
            )

    def test_execute_plan_returns_empty_when_no_changes(self) -> None:
        """Plan execution should report no modified files when all are compliant."""
        with TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            path = root / "config.ini"
            path.write_text("python=3.11\n", encoding="utf-8")

            rule = RegexRule(
                name="python",
                file_glob="*.ini",
                pattern=r"python=(?P<version>\d+\.\d+)",
                version="3.11",
            )

            plan = build_execution_plan([path], [rule])

            self.assertEqual(execute_plan(plan), [])

    def test_execute_plan_xml_only_rule_marks_file_modified(self) -> None:
        """Plan execution should process XML-only rule groups."""
        with TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            path = root / "project.xml"
            path.write_text(
                '<Project><Sdk Name="A" Version="1.0.0" /></Project>',
                encoding="utf-8",
            )

            rule = XmlRule(
                name="sdk",
                file_glob="*.xml",
                package="A",
                version="3.0.0",
            )

            plan = build_execution_plan([path], [rule])

            self.assertEqual(execute_plan(plan), [path])
