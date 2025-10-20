"""
Import Plugin for OpenSCENARIO Builder
Handles importing scenarios from various formats
"""

from typing import List, Optional
from xml.etree.ElementTree import Element as XMLElement, parse

try:
    from .plugin_metadata import PluginMetadata
except ImportError:
    # Fallback for when loaded directly by plugin manager
    from openscenario_builder.core.plugins.plugin_metadata import PluginMetadata

from openscenario_builder.interfaces import IImportPlugin, IElement
from openscenario_builder.core.model.element import Element


class ImportPlugin(IImportPlugin):
    """Plugin for importing scenarios from XML format"""

    def __init__(self):
        self._activated = True  # Default to activated

    @property
    def activated(self) -> bool:
        """Whether this plugin is activated and should be loaded"""
        return self._activated

    @activated.setter
    def activated(self, value: bool) -> None:
        """Set the activation state of this plugin"""
        self._activated = value

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="XML Import Plugin",
            version="1.0.0",
            description="Imports scenarios from OpenSCENARIO XML format",
            author="OpenSCENARIO Builder",
            license="MIT",
            tags=["import", "xml", "openscenario"],
        )

    def import_scenario(self, file_path: str) -> Optional[IElement]:
        """Import scenario from XML file"""
        try:
            # Parse the XML file
            tree = parse(file_path)
            root_etree = tree.getroot()

            # Convert XML ElementTree to custom Element
            root_element = self._xml_to_element(root_etree)

            return root_element

        except Exception as e:
            print(f"Import failed: {e}")
            return None

    def get_supported_formats(self) -> List[str]:
        """Return list of supported file extensions"""
        return [".xosc", ".xml"]

    def get_format_description(self, format_ext: str) -> str:
        """Return description for a specific format"""
        if format_ext == ".xosc":
            return "OpenSCENARIO XML format (.xosc)"
        elif format_ext == ".xml":
            return "Standard XML format (.xml)"
        return f"Import from {format_ext.upper()} format"

    def _xml_to_element(self, xml_element: XMLElement) -> Element:
        """Convert XML ElementTree element to custom Element"""
        # Extract attributes
        attrs = {}
        for key, value in xml_element.attrib.items():
            attrs[key] = value

        # Create element
        element = Element(xml_element.tag, attrs)

        # Process child elements recursively
        for child_xml in xml_element:
            child_element = self._xml_to_element(child_xml)
            element.add_child(child_element)

        return element
