"""
Plugin System for OpenSCENARIO Builder
Provides base classes and interfaces for the plugin system
"""

from typing import List, Optional
from openscenario_builder.interfaces import IPluginMetadata


class PluginMetadata(IPluginMetadata):
    """Metadata for a plugin"""

    def __init__(
        self,
        name: str,
        version: str,
        description: str,
        author: str,
        license: str = "MIT",
        homepage: str = "",
        dependencies: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
    ):
        self._name = name
        self._version = version
        self._description = description
        self._author = author
        self._license = license
        self._homepage = homepage
        self._dependencies = dependencies or []
        self._tags = tags or []

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return self._version

    @property
    def description(self) -> str:
        return self._description

    @property
    def author(self) -> str:
        return self._author

    @property
    def license(self) -> str:
        return self._license

    @property
    def homepage(self) -> str:
        return self._homepage

    @property
    def dependencies(self) -> Optional[List[str]]:
        return self._dependencies

    @property
    def tags(self) -> Optional[List[str]]:
        return self._tags
