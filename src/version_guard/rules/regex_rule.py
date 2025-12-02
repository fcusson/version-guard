"""A Version Guard rule for regex parsing."""

from pathlib import Path
import re
from re import Match

from version_guard.exceptions import FileChangedException

from version_guard.rules.base import Rule


class RegexRule(Rule):
    """A Version Guard rule for regex parsing."""

    def __init__(
        self,
        name: str,
        file_glob: str,
        pattern: str,
        version: str,
    ) -> None:
        """A Version Guard rule for regex parsing."""
        super().__init__(name, file_glob, version)

        self.pattern = re.compile(pattern)

    def replace_version(self, match: Match[str]) -> str:
        """Replaces the version in a match.

        Expected to be used with re.sub.
        """
        full = match.group(0)

        if match.group("version") == self.version:
            return full

        start, end = match.span("version")

        new = (
            full[: start - match.start()]
            + self.version
            + full[end - match.start() :]
        )

        return new

    def parse_file(self, path: Path) -> None:
        """Parses a file and updates it if needed.

        Raises:
            FileChangedException: The file was changed during
                processing.
            ParsingException: The file could not get parsed properly.
        """
        if not path.match(self.file_glob):
            return

        with path.open(mode="r") as file:
            content = file.read()

        modified = self.pattern.sub(self.replace_version, content)

        if modified != content:
            with path.open(mode="w") as file:
                file.write(modified)

            self.git_add(path)
            raise FileChangedException(path)
