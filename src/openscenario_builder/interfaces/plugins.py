"""
Plugin interface definitions for OpenSCENARIO Builder
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Protocol
from .model import IElement
from .schema import ISchemaInfo


class IPluginMetadata(Protocol):
    """Protocol for plugin metadata structure"""
    name: str
    version: str
    description: str
    author: str
    license: str
    homepage: str
    dependencies: Optional[List[str]]
    tags: Optional[List[str]]


class IBasePlugin(ABC):
    """Base interface for all plugins with activation control"""

    @property
    @abstractmethod
    def activated(self) -> bool:
        """Whether this plugin is activated and should be loaded"""
        pass

    @activated.setter
    @abstractmethod
    def activated(self, value: bool) -> None:
        """Set the activation state of this plugin"""
        pass


class IElementPlugin(IBasePlugin):
    """Base interface for custom element plugins"""

    @property
    @abstractmethod
    def metadata(self) -> IPluginMetadata:
        """Plugin metadata"""
        pass

    @abstractmethod
    def get_element_name(self) -> str:
        """Return the XML element name this plugin handles"""
        pass

    @abstractmethod
    def get_attributes(self) -> List[Dict[str, str]]:
        """Return list of attribute definitions"""
        pass

    @abstractmethod
    def get_allowed_children(self) -> List[str]:
        """Return list of allowed child element names"""
        pass

    def validate_element(self, element: IElement) -> List[str]:
        """Validate an element instance, return list of errors"""
        return []

    def get_description(self) -> str:
        """Return human-readable description of this element"""
        return f"Custom element: {self.get_element_name()}"

    def get_examples(self) -> List[Dict[str, Any]]:
        """Return example configurations"""
        return []


class IValidatorPlugin(IBasePlugin):
    """Base interface for custom validation plugins"""

    @property
    @abstractmethod
    def metadata(self) -> IPluginMetadata:
        """Plugin metadata"""
        pass

    @abstractmethod
    def validate_element(self, element: IElement, schema_info: Optional[ISchemaInfo] = None) -> List[str]:
        """Validate an element, optionally against the schema, return list of errors"""
        pass

    def get_name(self) -> str:
        """Return validator name"""
        return self.metadata.name

    def get_description(self) -> str:
        """Return validator description"""
        return self.metadata.description


class IUIPlugin(IBasePlugin):
    """Base interface for custom UI plugins"""

    @property
    @abstractmethod
    def metadata(self) -> IPluginMetadata:
        """Plugin metadata"""
        pass

    @abstractmethod
    def create_widget(self, parent=None) -> Any:
        """Create and return a UI widget"""
        pass

    def get_widget_name(self) -> str:
        """Return widget name for UI display"""
        return self.metadata.name


class IExportPlugin(IBasePlugin):
    """Base interface for custom export plugins"""

    @property
    @abstractmethod
    def metadata(self) -> IPluginMetadata:
        """Plugin metadata"""
        pass

    @abstractmethod
    def export_scenario(self, scenario: IElement, output_path: str) -> bool:
        """Export scenario to the specified format"""
        pass

    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """Return list of supported file extensions"""
        pass

    def get_format_description(self, format_ext: str) -> str:
        """Return description for a specific format"""
        return f"Export to {format_ext.upper()} format"


class IImportPlugin(IBasePlugin):
    """Base interface for custom import plugins"""

    @property
    @abstractmethod
    def metadata(self) -> IPluginMetadata:
        """Plugin metadata"""
        pass

    @abstractmethod
    def import_scenario(self, file_path: str) -> Optional[IElement]:
        """Import scenario from file, return Element or None if failed"""
        pass

    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """Return list of supported file extensions"""
        pass

    def get_format_description(self, format_ext: str) -> str:
        """Return description for a specific format"""
        return f"Import from {format_ext.upper()} format"
