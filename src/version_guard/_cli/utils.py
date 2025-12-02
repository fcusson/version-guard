"""Utility function for the cli."""

from pathlib import Path
from os.path import expandvars


def expand_path(path: str | Path) -> Path:
    """Expands user home and variable in a path or string."""
    path = expandvars(str(path))
    path = Path(path).expanduser()

    return path
