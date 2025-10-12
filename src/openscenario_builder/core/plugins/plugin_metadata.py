"""
Plugin System for OpenSCENARIO Builder
Provides base classes and interfaces for the plugin system
"""

from typing import List, Optional
from dataclasses import dataclass
from openscenario_builder.interfaces import IPluginMetadata


@dataclass
class PluginMetadata(IPluginMetadata):
    """Metadata for a plugin"""
    name: str
    version: str
    description: str
    author: str
    license: str = "MIT"
    homepage: str = ""
    dependencies: Optional[List[str]] = None
    tags: Optional[List[str]] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.tags is None:
            self.tags = []
