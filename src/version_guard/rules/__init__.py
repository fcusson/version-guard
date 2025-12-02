"""Module for the Version Guard Rules classes."""

from collections.abc import Iterator
from typing import cast

from version_guard.config import Rule as RuleDict, TypelessRule

from .base import Rule
from .regex_rule import RegexRule
from .xml_rule import XmlRule

RULE_TYPES: dict[str, type[Rule]] = {
    "regex": RegexRule,
    "xml": XmlRule,
}


def get_rules(rules: list[RuleDict]) -> Iterator[Rule]:
    """Builds rules based on their types."""
    for rule in rules:
        rule_type = rule.pop("type")
        yield RULE_TYPES[rule_type](**cast("TypelessRule", rule))


__all__ = [
    "get_rules",
    "Rule",
]
