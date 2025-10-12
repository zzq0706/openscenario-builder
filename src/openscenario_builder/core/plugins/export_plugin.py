"""
Export Plugin for OpenSCENARIO Builder
Handles exporting scenarios to various formats
"""

from typing import List
from pathlib import Path
from xml.etree.ElementTree import ElementTree, tostring
from xml.dom import minidom

try:
    from .plugin_metadata import PluginMetadata
except ImportError:
    # Fallback for when loaded directly by plugin manager
    from openscenario_builder.core.plugins.plugin_metadata import PluginMetadata

from openscenario_builder.interfaces import IExportPlugin, IElement


class ExportPlugin(IExportPlugin):
    """Plugin for exporting scenarios to XML format"""

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
            name="XML Export Plugin",
            version="1.0.0",
            description="Exports scenarios to OpenSCENARIO XML format",
            author="OpenSCENARIO Builder",
            license="MIT",
            tags=["export", "xml", "openscenario"]
        )

    def export_scenario(self, scenario: IElement, output_path: str) -> bool:
        """Export scenario to XML format"""
        try:
            # Use the Element's built-in XML conversion which handles namespaces properly
            formatted_xml = scenario.to_xml_string(pretty=True, encoding='unicode')

            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(formatted_xml)

            return True

        except Exception as e:
            print(f"Export failed: {e}")
            return False

    def get_supported_formats(self) -> List[str]:
        """Return list of supported file extensions"""
        return [".xosc", ".xml"]

    def get_format_description(self, format_ext: str) -> str:
        """Return description for a specific format"""
        if format_ext == ".xosc":
            return "OpenSCENARIO XML format (.xosc)"
        elif format_ext == ".xml":
            return "Standard XML format (.xml)"
        return f"Export to {format_ext.upper()} format"

    def _element_to_xml(self, element: IElement) -> 'xml.etree.ElementTree.Element':
        """Convert an Element to XML ElementTree element"""
        from xml.etree.ElementTree import Element

        # Create XML element with tag and attributes
        xml_elem = Element(element.tag, element.attrs)

        # Add child elements recursively
        for child in element.children:
            child_xml = self._element_to_xml(child)
            xml_elem.append(child_xml)

        return xml_elem
