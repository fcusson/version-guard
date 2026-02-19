"""Unit tests for configuration loading."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from version_guard.config import load_config


class ConfigTests(unittest.TestCase):
    """Tests for config file parsing."""

    def test_load_config_returns_rules(self) -> None:
        """YAML config should be loaded into the expected shape."""
        data = """
rules:
  - name: python
    type: regex
    file_glob: pyproject.toml
    pattern: 'python = "(?P<version>.*)"'
    version: "3.11"
"""

        with TemporaryDirectory() as tempdir:
            path = Path(tempdir) / "config.yaml"
            path.write_text(data, encoding="utf-8")

            config = load_config(path)

        self.assertEqual(len(config["rules"]), 1)
        self.assertEqual(config["rules"][0]["name"], "python")
        self.assertEqual(config["rules"][0]["version"], "3.11")


if __name__ == "__main__":
    unittest.main()
