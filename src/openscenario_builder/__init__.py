"""
OpenSCENARIO Builder Package
"""

__version__ = "1.0.0"
__author__ = "OpenSCENARIO Builder Team"

# Import main components for easy access
from .interfaces import *
from .core.model.element import Element
from .core.schema.parser import parse_openscenario_schema, SchemaInfo
from .core.plugins.plugin_manager import PluginManager

__all__ = [
    # Core interfaces
    "IElementDefinition",
    "IGroupDefinition",
    "ISchemaInfo",
    "XSDParser",
    "parse_openscenario_schema",
    # Model classes
    "Element",
    "SchemaInfo",
    # Plugin system
    "PluginManager",
]
