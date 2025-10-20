"""
Schema interface definitions for OpenSCENARIO Builder
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Mapping


class IChildElementInfo(ABC):
    """Abstract base class for child element occurrence information"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Element name"""
        pass

    @property
    @abstractmethod
    def min_occur(self) -> int:
        """Minimum occurrences"""
        pass

    @property
    @abstractmethod
    def max_occur(self) -> str:
        """Maximum occurrences (can be 'unbounded')"""
        pass


class IAttributeDefinition(ABC):
    """Abstract base class for attribute definition structure"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Attribute name"""
        pass

    @property
    @abstractmethod
    def type(self) -> str:
        """Attribute type"""
        pass

    @property
    @abstractmethod
    def required(self) -> bool:
        """Whether attribute is required"""
        pass


class IElementDefinition(ABC):
    """Abstract base class for element definition structure"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Element name"""
        pass

    @property
    @abstractmethod
    def attributes(self) -> List[IAttributeDefinition]:
        """Element attributes"""
        pass

    @property
    @abstractmethod
    def children(self) -> List[str]:
        """Allowed child element names"""
        pass

    @property
    @abstractmethod
    def is_abstract(self) -> bool:
        """Whether element is abstract"""
        pass

    @property
    @abstractmethod
    def is_root(self) -> bool:
        """Whether element is a root element"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Element description"""
        pass

    @property
    @abstractmethod
    def child_occurrence_info(self) -> Dict[str, IChildElementInfo]:
        """Child occurrence information"""
        pass

    @property
    @abstractmethod
    def content_model_type(self) -> str:
        """Content model type (sequence, choice, all)"""
        pass


class IGroupDefinition(ABC):
    """Abstract base class for group definition structure"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Group name"""
        pass

    @property
    @abstractmethod
    def children(self) -> List[str]:
        """Child element names"""
        pass

    @property
    @abstractmethod
    def is_choice(self) -> bool:
        """Whether group is a choice group"""
        pass

    @property
    @abstractmethod
    def is_sequence(self) -> bool:
        """Whether group is a sequence group"""
        pass

    @property
    @abstractmethod
    def is_all(self) -> bool:
        """Whether group is an all group"""
        pass

    @property
    @abstractmethod
    def child_occurrence_info(self) -> Dict[str, IChildElementInfo]:
        """Child occurrence information"""
        pass


class ISchemaInfo(ABC):
    """Abstract base class for schema information structure"""

    @property
    @abstractmethod
    def elements(self) -> Mapping[str, IElementDefinition]:
        """All element definitions"""
        pass

    @property
    @abstractmethod
    def groups(self) -> Mapping[str, IGroupDefinition]:
        """All group definitions"""
        pass

    @property
    @abstractmethod
    def root_elements(self) -> List[str]:
        """Root element names"""
        pass

    @property
    @abstractmethod
    def element_hierarchy(self) -> Dict[str, List[str]]:
        """Element hierarchy mapping"""
        pass

    @property
    @abstractmethod
    def simple_type_definitions(self) -> Dict[str, List[str]]:
        """Simple type definitions"""
        pass
