"""Entry point of the application."""

import logging
from logging import basicConfig, getLogger
from pathlib import Path
import sys

from ._cli.args import get_args
from .config import load_config
from .exceptions import FileChangedException
from .rules import get_rules, Rule

basicConfig(level=logging.INFO)
LOGGER = getLogger("version_guard")


def main() -> None:
    """Entry point of the application."""
    cli_config = get_args()
    config = load_config(cli_config["config"])

    LOGGER.info("parsing %d files", len(cli_config["files"]))
    LOGGER.info("Running %d rules", len(config["rules"]))

    for rule in get_rules(config["rules"]):
        LOGGER.info(f"Parsing files with rule `{repr(rule)}`")
        _parse_files(rule, cli_config["files"])


def _parse_files(rule: Rule, files: list[Path]) -> None:
    """Parses all the files."""
    modified = []

    for file in files:
        try:
            rule.parse_file(file)
        except FileChangedException:
            modified.append(file)

    if len(modified) > 0:
        LOGGER.info("The following files where modified:")
        for file in modified:
            LOGGER.info(f"- {str(file)}")
        sys.exit(1)
    else:
        LOGGER.info("No file modified")


if __name__ == "__main__":  # pragma: no cover
    main()
