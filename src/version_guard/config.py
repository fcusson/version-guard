"""Format of the configuration file."""

from pathlib import Path
from typing import TypedDict, Literal, cast, NotRequired

import yaml

RuleType = Literal["xml", "regex"]


class Rule(TypedDict):
    """A version guard rule."""

    name: str
    file_glob: str
    type: NotRequired[RuleType]
    version: str


class TypelessRule(TypedDict):
    """A version guard rule without the type key."""

    name: str
    file_glob: str
    version: str


class XmlRule(Rule):
    """An XML based Version Guard rule."""

    package: str
    element_name: NotRequired[str]
    name_attr: NotRequired[str]
    version_attr: NotRequired[str]


class RegexRule(Rule):
    """A regex based Version Guard rule."""

    pattern: str


class VersionGuardConfig(TypedDict):
    """The configuration for Version Guard."""

    rules: list[Rule]


def load_config(path: Path) -> VersionGuardConfig:
    """Retrieves the config from the path provided."""
    with path.open(mode="r") as file:
        config = yaml.safe_load(file)

    return cast("VersionGuardConfig", config)
