"""Unit tests for CLI argument parsing and helpers."""

from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from version_guard._cli.args import get_args
from version_guard._cli.utils import expand_path


class CliTests(unittest.TestCase):
    """Tests for CLI helpers."""

    def test_expand_path_expands_env_var(self) -> None:
        """Environment variables should be expanded in paths."""
        with patch.dict("os.environ", {"VG_TEST_DIR": "/tmp/version-guard"}):
            expanded = expand_path("$VG_TEST_DIR/config.yaml")

        self.assertEqual(expanded, Path("/tmp/version-guard/config.yaml"))

    def test_get_args_defaults(self) -> None:
        """Default args should be returned when no arguments are provided."""
        with patch.object(sys, "argv", ["version-guard"]):
            args = get_args()

        self.assertEqual(args["files"], [])
        self.assertEqual(args["config"], Path(".version-guard.yaml"))
        self.assertEqual(args["workdir"], Path.cwd())
        self.assertFalse(args["force"])

    def test_get_args_custom_values(self) -> None:
        """Custom CLI values should be parsed properly."""
        argv = [
            "version-guard",
            "pyproject.toml",
            "README.md",
            "--config",
            "./custom.yaml",
            "--workdir",
            "/tmp",
            "--force",
        ]

        with patch.object(sys, "argv", argv):
            args = get_args()

        self.assertEqual(
            args["files"],
            [Path("pyproject.toml"), Path("README.md")],
        )
        self.assertEqual(args["config"], Path("custom.yaml"))
        self.assertEqual(args["workdir"], Path("/tmp"))
        self.assertTrue(args["force"])


if __name__ == "__main__":
    unittest.main()
