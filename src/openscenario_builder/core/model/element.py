"""
Enhanced Element Model for OpenSCENARIO Builder
Provides a robust, validated element structure with metadata support
"""

from openscenario_builder.interfaces import ISchemaInfo, IElement, IElementMetadata
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from xml.etree.ElementTree import Element as XMLElement, SubElement, tostring
from xml.dom import minidom
from datetime import datetime


@dataclass
class ElementMetadata(IElementMetadata):
    """Metadata for an element"""
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)
    validation_errors: List[str] = field(default_factory=list)


class Element(IElement):
    """
    Enhanced Element class with validation, metadata, and XML handling
    """

    def __init__(self, tag: str, attrs: Optional[Dict[str, str]] = None,
                 children: Optional[List['Element']] = None,
                 metadata: Optional[ElementMetadata] = None):
        self.tag = tag
        self.attrs = attrs or {}
        self.children = children or []
        self.metadata = metadata or ElementMetadata()

    @property
    def id(self) -> str:
        """Unique identifier for this element"""
        return self._id

    def add_child(self, child: 'Element') -> None:
        """Add a child element"""
        if child not in self.children:
            self.children.append(child)
            self.metadata.modified_at = datetime.now()

    def remove_child(self, child: 'Element') -> bool:
        """Remove a child element, returns True if found and removed"""
        if child in self.children:
            self.children.remove(child)
            self.metadata.modified_at = datetime.now()
            return True
        return False

    def insert_child(self, index: int, child: 'Element') -> None:
        """Insert a child element at a specific index"""
        if child not in self.children:
            self.children.insert(index, child)
            self.metadata.modified_at = datetime.now()

    def get_child_by_tag(self, tag: str) -> Optional['Element']:
        """Get the first child element with the specified tag"""
        for child in self.children:
            if child.tag == tag:
                return child
        return None

    def get_children_by_tag(self, tag: str) -> List['Element']:
        """Get all child elements with the specified tag"""
        return [child for child in self.children if child.tag == tag]

    def set_attribute(self, name: str, value: str) -> None:
        """Set an attribute value"""
        self.attrs[name] = value
        self.metadata.modified_at = datetime.now()

    def get_attribute(self, name: str, default: str = "") -> str:
        """Get an attribute value"""
        return self.attrs.get(name, default)

    def remove_attribute(self, name: str) -> bool:
        """Remove an attribute, returns True if found and removed"""
        if name in self.attrs:
            del self.attrs[name]
            self.metadata.modified_at = datetime.now()
            return True
        return False

    def has_attribute(self, name: str) -> bool:
        """Check if element has a specific attribute"""
        return name in self.attrs

    def to_etree_element(self) -> XMLElement:
        """Convert to XML ElementTree element"""
        elem = XMLElement(self.tag, {k: str(v) for k, v in self.attrs.items()})
        for child in self.children:
            elem.append(child.to_etree_element())
        return elem

    def to_xml_string(self, pretty: bool = True, encoding: str = 'unicode') -> str:
        """Convert to XML string"""
        try:
            # Convert to ElementTree first
            etree_elem = self.to_etree_element()

            # Convert to string
            if pretty:
                # Pretty print with indentation using a cleaner approach
                rough_string = tostring(etree_elem, encoding=encoding)

                # Clean up any namespace prefixes that might have been added
                rough_string = self._clean_namespace_prefixes(rough_string)

                reparsed = minidom.parseString(rough_string)
                pretty_xml = reparsed.toprettyxml(indent="  ")

                # Clean up any remaining namespace prefixes
                pretty_xml = self._clean_namespace_prefixes(pretty_xml)

                return pretty_xml.strip()
            else:
                # Compact output
                xml_string = tostring(etree_elem, encoding=encoding)
                return self._clean_namespace_prefixes(xml_string)

        except Exception as e:
            raise ValueError(f"Failed to convert to XML string: {e}")

    def _clean_namespace_prefixes(self, xml_string: str) -> str:
        """Remove unwanted namespace prefixes from XML string"""
        import re
        # Remove namespace prefixes like ns0:, ns1:, etc.
        xml_string = re.sub(r'\bns\d+:', '', xml_string)
        # Remove namespace declarations that are no longer needed
        xml_string = re.sub(r'\s+xmlns:ns\d+="[^"]*"', '', xml_string)
        return xml_string

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "tag": self.tag,
            "attrs": self.attrs,
            "children": [child.to_dict() for child in self.children],
            "metadata": {
                "created_at": self.metadata.created_at.isoformat(),
                "modified_at": self.metadata.modified_at.isoformat(),
                "created_by": self.metadata.created_by,
                "description": self.metadata.description,
                "tags": self.metadata.tags
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Element':
        """Create Element from dictionary representation"""
        element = cls(
            tag=data["tag"],
            attrs=data.get("attrs", {}),
            metadata=ElementMetadata(
                created_at=datetime.fromisoformat(
                    data["metadata"]["created_at"]),
                modified_at=datetime.fromisoformat(
                    data["metadata"]["modified_at"]),
                created_by=data["metadata"]["created_by"],
                description=data["metadata"]["description"],
                tags=data["metadata"]["tags"]
            )
        )

        # Add children recursively
        for child_data in data.get("children", []):
            child = cls.from_dict(child_data)
            element.add_child(child)

        return element

    @classmethod
    def from_etree_element(cls, etree_elem: XMLElement) -> 'Element':
        """Create Element from XML ElementTree element"""
        element = cls(
            tag=etree_elem.tag,
            attrs=dict(etree_elem.attrib)
        )

        # Add children recursively
        for child_elem in etree_elem:
            child = cls.from_etree_element(child_elem)
            element.add_child(child)

        return element

    def clone(self) -> 'Element':
        """Create a deep copy of this element"""
        return self.from_dict(self.to_dict())

    def find_elements_by_tag(self, tag: str) -> List['Element']:
        """Find all elements with the specified tag in the subtree"""
        results = []
        if self.tag == tag:
            results.append(self)

        for child in self.children:
            results.extend(child.find_elements_by_tag(tag))

        return results

    def __str__(self) -> str:
        """String representation"""
        attrs_str = " ".join([f'{k}="{v}"' for k, v in self.attrs.items()])
        return f"<{self.tag} {attrs_str}> ({len(self.children)} children)"

    def __repr__(self) -> str:
        """Detailed representation"""
        return f"Element(tag='{self.tag}', attrs={self.attrs}, children={len(self.children)})"
