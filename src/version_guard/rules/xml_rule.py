"""A Version Guard rule for xml parsing."""

from collections.abc import Iterator
from logging import getLogger
from pathlib import Path
from xml.etree.ElementTree import ElementTree, Element  # nosec

from version_guard.exceptions import FileChangedException

from .base import Rule


LOGGER = getLogger(__name__)


class XmlRule(Rule):
    """A Version Guard rule for xml parsing."""

    def __init__(
        self,
        name: str,
        file_glob: str,
        package: str,
        version: str,
        element_name: str = "Sdk",
        name_attr: str = "Name",
        version_attr: str = "Version",
    ) -> None:
        """A Version Guard rule for xml parsing."""
        super().__init__(name, file_glob, version)

        self.package = package
        self.element_name = element_name
        self.name_attr = name_attr
        self.version_attr = version_attr

    def __repr__(self) -> str:
        """Internal Repsentation of the rule."""
        return (
            f"<XmlRule glob=`{self.file_glob}`, package=`{self.package}`,"
            f" version=`{self.version}`>"
        )

    def get_version_nodes(self, root: Element) -> Iterator[Element]:
        """Returns an Iterator of all elements that fit the version config."""
        for child in root.findall(path=self.element_name):
            if child.attrib.get(self.name_attr) == self.package:
                yield child

    def parse_file(self, path: Path) -> None:
        """Parses a file and updates it if needed.

        Raises:
            FileChangedException: The file was changed during
                processing.
            ParsingException: The file could not get parsed properly.
        """
        if not path.match(self.file_glob):
            return

        element_tree = ElementTree(file=path)
        root = element_tree.getroot()

        any_changes = False

        for version_element in self.get_version_nodes(root):
            current_version = version_element.attrib.get(self.version_attr)

            if self.invalid_version(current_version):
                version_element.set(self.version_attr, self.version)
                any_changes = True

        if any_changes:
            element_tree.write(path)
            LOGGER.info(f"`{str(path)}` was modified")
            raise FileChangedException(path)
        else:
            LOGGER.info(f"`{str(path)}` unchanged")
