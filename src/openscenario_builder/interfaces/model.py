"""
Model interface definitions for OpenSCENARIO Builder
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime


class IElementMetadata(ABC):
    """Abstract base class for element metadata structure"""
    
    @property
    @abstractmethod
    def created_at(self) -> datetime:
        """Creation timestamp"""
        pass
    
    @property
    @abstractmethod
    def modified_at(self) -> datetime:
        """Last modification timestamp"""
        pass
    
    @property
    @abstractmethod
    def created_by(self) -> str:
        """Creator identifier"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Element description"""
        pass
    
    @property
    @abstractmethod
    def tags(self) -> List[str]:
        """Element tags"""
        pass
    
    @property
    @abstractmethod
    def validation_errors(self) -> List[str]:
        """Validation errors"""
        pass


class IElement(ABC):
    """Abstract base class for element structure"""
    
    @property
    @abstractmethod
    def tag(self) -> str:
        """Element tag name"""
        pass
    
    @property
    @abstractmethod
    def attrs(self) -> Dict[str, str]:
        """Element attributes"""
        pass
    
    @property
    @abstractmethod
    def children(self) -> List['IElement']:
        """Child elements"""
        pass
    
    @property
    @abstractmethod
    def metadata(self) -> IElementMetadata:
        """Element metadata"""
        pass

    @abstractmethod
    def add_child(self, child: 'IElement') -> None:
        """Add a child element"""
        pass

    @abstractmethod
    def remove_child(self, child: 'IElement') -> bool:
        """Remove a child element, returns True if found and removed"""
        pass

    @abstractmethod
    def insert_child(self, index: int, child: 'IElement') -> None:
        """Insert a child element at a specific index"""
        pass

    @abstractmethod
    def get_child_by_tag(self, tag: str) -> Optional['IElement']:
        """Get the first child element with the specified tag"""
        pass

    @abstractmethod
    def get_children_by_tag(self, tag: str) -> List['IElement']:
        """Get all child elements with the specified tag"""
        pass

    @abstractmethod
    def set_attribute(self, name: str, value: str) -> None:
        """Set an attribute value"""
        pass

    @abstractmethod
    def get_attribute(self, name: str, default: str = "") -> str:
        """Get an attribute value"""
        pass

    @abstractmethod
    def remove_attribute(self, name: str) -> bool:
        """Remove an attribute, returns True if found and removed"""
        pass

    @abstractmethod
    def has_attribute(self, name: str) -> bool:
        """Check if element has a specific attribute"""
        pass

    @abstractmethod
    def to_etree_element(self) -> Any:
        """Convert to XML ElementTree element"""
        pass

    @abstractmethod
    def to_xml_string(self, pretty: bool = True, encoding: str = 'unicode') -> str:
        """Convert to XML string"""
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IElement':
        """Create Element from dictionary representation"""
        pass

    @classmethod
    @abstractmethod
    def from_etree_element(cls, etree_elem: Any) -> 'IElement':
        """Create Element from XML ElementTree element"""
        pass

    @abstractmethod
    def clone(self) -> 'IElement':
        """Create a deep copy of this element"""
        pass

    @abstractmethod
    def find_elements_by_tag(self, tag: str) -> List['IElement']:
        """Find all elements with the specified tag in the subtree"""
        pass
