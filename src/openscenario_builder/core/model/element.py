"""
Enhanced Element Model for OpenSCENARIO Builder
Provides a robust, validated element structure with metadata support
"""

from openscenario_builder.interfaces import ISchemaInfo, IElement, IElementMetadata
from typing import Dict, List, Optional, Any, Union
from xml.etree.ElementTree import Element as XMLElement, SubElement, tostring
from xml.dom import minidom
from datetime import datetime


class ElementMetadata(IElementMetadata):
    """Metadata for an element"""
    
    def __init__(
        self,
        created_at: Optional[datetime] = None,
        modified_at: Optional[datetime] = None,
        created_by: str = "",
        description: str = "",
        tags: Optional[List[str]] = None,
        validation_errors: Optional[List[str]] = None
    ):
        self._created_at = created_at or datetime.now()
        self._modified_at = modified_at or datetime.now()
        self._created_by = created_by
        self._description = description
        self._tags = tags or []
        self._validation_errors = validation_errors or []
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def modified_at(self) -> datetime:
        return self._modified_at
    
    @modified_at.setter
    def modified_at(self, value: datetime) -> None:
        self._modified_at = value
    
    @property
    def created_by(self) -> str:
        return self._created_by
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def tags(self) -> List[str]:
        return self._tags
    
    @property
    def validation_errors(self) -> List[str]:
        return self._validation_errors


class Element(IElement):
    """
    Enhanced Element class with validation, metadata, and XML handling
    """

    def __init__(self, tag: str, attrs: Optional[Dict[str, str]] = None,
                 children: Optional[List[IElement]] = None,
                 metadata: Optional[ElementMetadata] = None):
        self._tag = tag
        self._attrs = attrs or {}
        self._children: List[IElement] = children or []
        self._metadata = metadata or ElementMetadata()
        self._id = f"{tag}_{id(self)}"
    
    @property
    def tag(self) -> str:
        """Element tag name"""
        return self._tag
    
    @property
    def attrs(self) -> Dict[str, str]:
        """Element attributes"""
        return self._attrs
    
    @property
    def children(self) -> List[IElement]:
        """Child elements"""
        return self._children
    
    @property
    def metadata(self) -> IElementMetadata:
        """Element metadata"""
        return self._metadata

    @property
    def id(self) -> str:
        """Unique identifier for this element"""
        return self._id

    def add_child(self, child: IElement) -> None:
        """Add a child element"""
        if child not in self._children:
            self._children.append(child)
            self._metadata.modified_at = datetime.now()

    def remove_child(self, child: IElement) -> bool:
        """Remove a child element, returns True if found and removed"""
        if child in self._children:
            self._children.remove(child)
            self._metadata.modified_at = datetime.now()
            return True
        return False

    def insert_child(self, index: int, child: IElement) -> None:
        """Insert a child element at a specific index"""
        if child not in self._children:
            self._children.insert(index, child)
            self._metadata.modified_at = datetime.now()

    def get_child_by_tag(self, tag: str) -> Optional[IElement]:
        """Get the first child element with the specified tag"""
        for child in self._children:
            if child.tag == tag:
                return child
        return None

    def get_children_by_tag(self, tag: str) -> List[IElement]:
        """Get all child elements with the specified tag"""
        return [child for child in self._children if child.tag == tag]

    def set_attribute(self, name: str, value: str) -> None:
        """Set an attribute value"""
        self._attrs[name] = value
        self._metadata.modified_at = datetime.now()

    def get_attribute(self, name: str, default: str = "") -> str:
        """Get an attribute value"""
        return self._attrs.get(name, default)

    def remove_attribute(self, name: str) -> bool:
        """Remove an attribute, returns True if found and removed"""
        if name in self._attrs:
            del self._attrs[name]
            self._metadata.modified_at = datetime.now()
            return True
        return False

    def has_attribute(self, name: str) -> bool:
        """Check if element has a specific attribute"""
        return name in self._attrs

    def to_etree_element(self) -> XMLElement:
        """Convert to XML ElementTree element"""
        elem = XMLElement(self._tag, {k: str(v) for k, v in self._attrs.items()})
        for child in self._children:
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
            "tag": self._tag,
            "attrs": self._attrs,
            "children": [child.to_dict() for child in self._children],
            "metadata": {
                "created_at": self._metadata.created_at.isoformat(),
                "modified_at": self._metadata.modified_at.isoformat(),
                "created_by": self._metadata.created_by,
                "description": self._metadata.description,
                "tags": self._metadata.tags
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

    def find_elements_by_tag(self, tag: str) -> List[IElement]:
        """Find all elements with the specified tag in the subtree"""
        results: List[IElement] = []
        if self._tag == tag:
            results.append(self)

        for child in self._children:
            results.extend(child.find_elements_by_tag(tag))

        return results

    def __str__(self) -> str:
        """String representation"""
        attrs_str = " ".join([f'{k}="{v}"' for k, v in self._attrs.items()])
        return f"<{self._tag} {attrs_str}> ({len(self._children)} children)"

    def __repr__(self) -> str:
        """Detailed representation"""
        return f"Element(tag='{self._tag}', attrs={self._attrs}, children={len(self._children)})"
