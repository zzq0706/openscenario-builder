"""
Interface definitions for OpenSCENARIO Builder
All interfaces are defined here to ensure complete decoupling from implementations
"""

from .schema import IElementDefinition, IGroupDefinition, ISchemaInfo, IAttributeDefinition, IChildElementInfo
from .plugins import IPluginMetadata, IElementPlugin, IValidatorPlugin, IUIPlugin, IExportPlugin, IImportPlugin
from .model import IElement, IElementMetadata

__all__ = [
    # Schema interfaces
    'IElementDefinition',
    'IGroupDefinition',
    'ISchemaInfo',
    'IAttributeDefinition',
    'IChildElementInfo',
    # Plugin interfaces
    'IPluginMetadata',
    'IElementPlugin',
    'IValidatorPlugin',
    'IUIPlugin',
    'IExportPlugin',
    'IImportPlugin',
    # Model interfaces
    'IElement',
    'IElementMetadata'
]
