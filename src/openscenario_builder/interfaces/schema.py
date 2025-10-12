"""
Schema interface definitions for OpenSCENARIO Builder
"""

from typing import Dict, List, Protocol, TypedDict


class IChildElementInfo(Protocol):
    """Protocol for child element occurrence information"""
    name: str
    min_occur: int
    max_occur: str


class IAttributeDefinition(Protocol):
    """Interface for attribute definition structure"""
    name: str
    type: str
    required: bool


class IElementDefinition(Protocol):
    """Protocol for element definition structure"""
    name: str
    attributes: List[IAttributeDefinition]
    children: List[str]
    is_abstract: bool
    is_root: bool
    description: str = ""
    child_occurrence_info: Dict[str, IChildElementInfo]
    content_model_type: str



class IGroupDefinition(Protocol):
    """Protocol for group definition structure"""
    name: str
    children: List[str]
    is_choice: bool
    is_sequence: bool
    is_all: bool
    child_occurrence_info: Dict[str, IChildElementInfo]


class ISchemaInfo(Protocol):
    """Protocol for schema information structure"""
    elements: Dict[str, IElementDefinition]
    groups: Dict[str, IGroupDefinition]
    root_elements: List[str]
    element_hierarchy: Dict[str, List[str]]
    simple_type_definitions: Dict[str, List[str]]
