"""A Version Guard rule."""

from abc import ABC, abstractmethod
from pathlib import Path
import subprocess  # nosec


class Rule(ABC):
    """A Version Guard rule."""

    def __init__(self, name: str, file_glob: str, version: str) -> None:
        """A Version Guard rule."""
        self.name = name.strip()
        self.file_glob = file_glob.strip()
        self.version = version.strip()

    def invalid_version(self, current: str) -> bool:
        """Returns True if the current version doesn't match target."""
        return current.strip() != self.version

    @staticmethod
    def git_add(path: Path) -> None:
        """Adds a file to git staging."""
        subprocess.run(["git", "add", str(path)], check=False)  # nosec

    @abstractmethod
    def parse_file(self, path: Path) -> None:
        """Parses a file and updates it if needed.

        Raises:
            FileChangedException: The file was changed during
                processing.
            ParsingException: The file could not get parsed properly.
        """
