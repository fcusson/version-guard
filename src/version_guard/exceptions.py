"""Exceptions for Version Guard."""

from pathlib import Path


class VersionGuardException(Exception):
    """Generic Exception for Version Guard."""


class FileChangedException(VersionGuardException):
    """Raised if a file is changed during version guard processing."""

    def __init__(self, path: Path) -> None:
        """Raised if a file is changed during version guard processing."""
        super().__init__(f"`{str(path)}` was modified.")


class ParsingException(VersionGuardException):
    """Raised if Version Guard was unable to parse a file."""
