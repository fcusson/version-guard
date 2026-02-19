"""Entry point of the application."""

import logging
from logging import basicConfig, getLogger
import sys

from ._cli.args import get_args
from .config import load_config
from .engine import build_execution_plan, discover_files_once, execute_plan
from .rules import get_rules

basicConfig(level=logging.INFO)
LOGGER = getLogger("version_guard")


def main() -> None:
    """Entry point of the application."""
    cli_config = get_args()
    config = load_config(cli_config["config"])
    rules = list(get_rules(config["rules"]))

    LOGGER.info("Running %d rules", len(rules))

    if cli_config["force"]:
        globs = {rule.file_glob for rule in rules}
        files = discover_files_once(cli_config["workdir"], globs)
    else:
        files = cli_config["files"]

    LOGGER.info("parsing %d files", len(files))

    plan = build_execution_plan(files, rules)
    modified = execute_plan(plan)

    if modified:
        LOGGER.info("The following files where modified:")
        for file in modified:
            LOGGER.info("- %s", str(file))
        sys.exit(1)

    LOGGER.info("No file modified")


if __name__ == "__main__":  # pragma: no cover
    main()
