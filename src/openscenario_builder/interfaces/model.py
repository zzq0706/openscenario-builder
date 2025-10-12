"""
Model interface definitions for OpenSCENARIO Builder
"""

from typing import Dict, List, Optional, Any, Protocol
from datetime import datetime


class IElementMetadata(Protocol):
    """Protocol for element metadata structure"""
    created_at: datetime
    modified_at: datetime
    created_by: str
    description: str
    tags: List[str]
    validation_errors: List[str]


class IElement(Protocol):
    """Protocol for element structure"""
    tag: str
    attrs: Dict[str, str]
    children: List['IElement']
    metadata: IElementMetadata
    id: str

    def add_child(self, child: 'IElement') -> None:
        """Add a child element"""
        ...

    def remove_child(self, child: 'IElement') -> bool:
        """Remove a child element, returns True if found and removed"""
        ...

    def insert_child(self, index: int, child: 'IElement') -> None:
        """Insert a child element at a specific index"""
        ...

    def get_child_by_tag(self, tag: str) -> Optional['IElement']:
        """Get the first child element with the specified tag"""
        ...

    def get_children_by_tag(self, tag: str) -> List['IElement']:
        """Get all child elements with the specified tag"""
        ...

    def set_attribute(self, name: str, value: str) -> None:
        """Set an attribute value"""
        ...

    def get_attribute(self, name: str, default: str = "") -> str:
        """Get an attribute value"""
        ...

    def remove_attribute(self, name: str) -> bool:
        """Remove an attribute, returns True if found and removed"""
        ...

    def has_attribute(self, name: str) -> bool:
        """Check if element has a specific attribute"""
        ...

    def to_etree_element(self) -> Any:
        """Convert to XML ElementTree element"""
        ...

    def to_xml_string(self, pretty: bool = True, encoding: str = 'unicode') -> str:
        """Convert to XML string"""
        ...

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        ...

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IElement':
        """Create Element from dictionary representation"""
        ...

    @classmethod
    def from_etree_element(cls, etree_elem: Any) -> 'IElement':
        """Create Element from XML ElementTree element"""
        ...

    def clone(self) -> 'IElement':
        """Create a deep copy of this element"""
        ...

    def find_element_by_id(self, element_id: str) -> Optional['IElement']:
        """Find an element by its ID in the subtree"""
        ...

    def find_elements_by_tag(self, tag: str) -> List['IElement']:
        """Find all elements with the specified tag in the subtree"""
        ...


# Forward reference to avoid circular import
ISchemaInfo = Any
