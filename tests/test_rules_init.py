"""Unit tests for rule factory functions."""

import unittest

from version_guard.rules import get_rules
from version_guard.rules.regex_rule import RegexRule
from version_guard.rules.xml_rule import XmlRule


class RuleFactoryTests(unittest.TestCase):
    """Tests for get_rules."""

    def test_get_rules_builds_typed_instances_without_mutation(self) -> None:
        """Rules should be instantiated with expected classes and no input mutation."""
        config_rules = [
            {
                "name": "python",
                "type": "regex",
                "file_glob": "*.toml",
                "pattern": 'python = "(?P<version>.*)"',
                "version": "3.11",
            },
            {
                "name": "sdk",
                "type": "xml",
                "file_glob": "*.xml",
                "package": "A",
                "version": "1.0.0",
            },
        ]

        original = [dict(item) for item in config_rules]
        rules = list(get_rules(config_rules))

        self.assertIsInstance(rules[0], RegexRule)
        self.assertIsInstance(rules[1], XmlRule)
        self.assertEqual(config_rules, original)


if __name__ == "__main__":
    unittest.main()
