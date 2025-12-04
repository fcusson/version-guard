"""Definition of the argparse configuration."""

from argparse import ArgumentParser
from pathlib import Path
from typing import TypedDict, cast

from .utils import expand_path


class CliConfig(TypedDict):
    """Configuration of the stdin arguments."""

    files: list[Path]
    config: Path
    force: bool
    workdir: Path


def get_args() -> CliConfig:
    """Retrieves the arguments from stdin."""
    parser = ArgumentParser(prog="version-guard")

    parser.add_argument(
        "files",
        nargs="*",
        help="Files to parse",
        type=expand_path,
        default=[],
    )

    parser.add_argument(
        "-c",
        "--config",
        help=(
            "Location of the configuration file. Defaults to "
            "./version-guard.yaml"
        ),
        type=expand_path,
        default=Path("./.version-guard.yaml"),
    )

    parser.add_argument(
        "-w",
        "--workdir",
        help="Working directory root. Defaults to current working directory.",
        type=expand_path,
        default=Path.cwd(),
    )

    parser.add_argument(
        "-f",
        "--force",
        help="Force all files matching to glob to be checked.",
        action="store_true",
    )

    config = cast("CliConfig", vars(parser.parse_args()))

    return config
