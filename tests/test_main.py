"""Unit tests for the application entry point."""

from pathlib import Path
import unittest
from unittest.mock import patch

from version_guard.__main__ import main


class MainTests(unittest.TestCase):
    """Tests for CLI execution orchestration."""

    @patch("version_guard.__main__.execute_plan")
    @patch("version_guard.__main__.build_execution_plan")
    @patch("version_guard.__main__.discover_files_once")
    @patch("version_guard.__main__.get_rules")
    @patch("version_guard.__main__.load_config")
    @patch("version_guard.__main__.get_args")
    def test_main_force_path_uses_single_discovery(
        self,
        get_args_mock,
        load_config_mock,
        get_rules_mock,
        discover_mock,
        build_plan_mock,
        execute_mock,
    ) -> None:
        """Force mode should trigger repository discovery and execution plan."""
        get_args_mock.return_value = {
            "files": [],
            "config": Path(".version-guard.yaml"),
            "force": True,
            "workdir": Path("/repo"),
        }
        load_config_mock.return_value = {"rules": [{"name": "r1"}]}

        class StubRule:
            file_glob = "*.toml"

        rules = [StubRule()]
        files = [Path("/repo/pyproject.toml")]

        get_rules_mock.return_value = iter(rules)
        discover_mock.return_value = files
        build_plan_mock.return_value = {files[0]: rules}
        execute_mock.return_value = []

        main()

        discover_mock.assert_called_once_with(Path("/repo"), {"*.toml"})
        build_plan_mock.assert_called_once_with(files, rules)
        execute_mock.assert_called_once()

    @patch("version_guard.__main__.execute_plan")
    @patch("version_guard.__main__.build_execution_plan")
    @patch("version_guard.__main__.discover_files_once")
    @patch("version_guard.__main__.get_rules")
    @patch("version_guard.__main__.load_config")
    @patch("version_guard.__main__.get_args")
    def test_main_non_force_uses_cli_files(
        self,
        get_args_mock,
        load_config_mock,
        get_rules_mock,
        discover_mock,
        build_plan_mock,
        execute_mock,
    ) -> None:
        """Non-force mode should skip discovery and use CLI file list."""
        cli_files = [Path("README.md")]
        get_args_mock.return_value = {
            "files": cli_files,
            "config": Path(".version-guard.yaml"),
            "force": False,
            "workdir": Path("/repo"),
        }
        load_config_mock.return_value = {"rules": [{"name": "r1"}]}
        get_rules_mock.return_value = iter([])
        build_plan_mock.return_value = {}
        execute_mock.return_value = []

        main()

        discover_mock.assert_not_called()
        build_plan_mock.assert_called_once_with(cli_files, [])

    @patch("version_guard.__main__.sys.exit", side_effect=SystemExit(1))
    @patch("version_guard.__main__.execute_plan")
    @patch("version_guard.__main__.build_execution_plan")
    @patch("version_guard.__main__.get_rules")
    @patch("version_guard.__main__.load_config")
    @patch("version_guard.__main__.get_args")
    def test_main_exits_when_files_modified(
        self,
        get_args_mock,
        load_config_mock,
        get_rules_mock,
        build_plan_mock,
        execute_mock,
        exit_mock,
    ) -> None:
        """Main should exit with code 1 when changes are made."""
        changed = Path("README.md")

        get_args_mock.return_value = {
            "files": [changed],
            "config": Path(".version-guard.yaml"),
            "force": False,
            "workdir": Path.cwd(),
        }
        load_config_mock.return_value = {"rules": []}
        get_rules_mock.return_value = iter([])
        build_plan_mock.return_value = {}
        execute_mock.return_value = [changed]

        with self.assertRaises(SystemExit):
            main()

        exit_mock.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main()
