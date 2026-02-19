"""Execution engine for Version Guard."""

from collections import defaultdict
from pathlib import Path
from collections.abc import Iterable
from xml.etree.ElementTree import ElementTree, Element  # nosec

from .exceptions import ParsingException
from .rules import Rule
from .rules.regex_rule import RegexRule
from .rules.xml_rule import XmlRule


def discover_files_once(root: Path, globs: set[str]) -> list[Path]:
    """Discovers matching files with a single repository walk."""
    files: list[Path] = []

    for path in root.rglob("*"):
        if not path.is_file():
            continue

        if any(path.match(glob) for glob in globs):
            files.append(path)

    return files


def build_execution_plan(
    files: Iterable[Path],
    rules: list[Rule],
) -> dict[Path, list[Rule]]:
    """Maps each file to all applicable rules."""
    plan: dict[Path, list[Rule]] = {}

    rules_by_glob: dict[str, list[Rule]] = defaultdict(list)
    for rule in rules:
        rules_by_glob[rule.file_glob].append(rule)

    for path in files:
        matching: list[Rule] = []

        for glob, glob_rules in rules_by_glob.items():
            if path.match(glob):
                matching.extend(glob_rules)

        if matching:
            plan[path] = matching

    return plan


def execute_plan(plan: dict[Path, list[Rule]]) -> list[Path]:
    """Executes all rule operations file-by-file and returns modified files."""
    modified_files: list[Path] = []

    for path, file_rules in plan.items():
        regex_rules = [x for x in file_rules if isinstance(x, RegexRule)]
        xml_rules = [x for x in file_rules if isinstance(x, XmlRule)]

        changed = False

        if regex_rules:
            changed = _apply_regex_rules(path, regex_rules) or changed

        if xml_rules:
            changed = _apply_xml_rules(path, xml_rules) or changed

        if changed:
            modified_files.append(path)

    return modified_files


def _apply_regex_rules(path: Path, rules: list[RegexRule]) -> bool:
    """Applies all regex rules to a file with a single read/write cycle."""
    with path.open(mode="r") as file:
        content = file.read()

    modified = content
    for rule in rules:
        modified = rule.pattern.sub(rule.replace_version, modified)

    if modified == content:
        return False

    with path.open(mode="w") as file:
        file.write(modified)

    return True


def _apply_xml_rules(path: Path, rules: list[XmlRule]) -> bool:
    """Applies all XML rules to a file with a single parse/write cycle."""
    element_tree = ElementTree(file=path)
    root = element_tree.getroot()
    if root is None:
        raise ParsingException(f"`{str(path)}` has no XML root element.")

    any_changes = False

    for rule in rules:
        for version_element in rule.get_version_nodes(root):
            if not isinstance(version_element, Element):
                continue

            current_version = version_element.attrib.get(rule.version_attr)

            if rule.invalid_version(current_version):
                version_element.set(rule.version_attr, rule.version)
                any_changes = True

    if not any_changes:
        return False

    element_tree.write(path)
    return True
