"""Module for the Version Guard Rules classes."""

from collections.abc import Iterator
from typing import cast

from version_guard.config import Rule as RuleDict, RuleType, TypelessRule

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
        rule_data = dict(rule)
        rule_type = cast("RuleType", rule_data.pop("type"))
        yield RULE_TYPES[rule_type](**cast("TypelessRule", rule_data))


__all__ = [
    "get_rules",
    "Rule",
]
