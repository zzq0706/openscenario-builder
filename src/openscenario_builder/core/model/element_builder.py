"""
Builder Pattern for Schema-Aware Element Construction
Provides fluent interface for creating validated OpenSCENARIO elements
"""

from typing import Dict, List, Optional
from openscenario_builder.interfaces import ISchemaInfo, IElement
from openscenario_builder.core.model.element_factory import ElementFactory


class ElementBuilder:
    """
    Fluent builder for creating schema-validated elements.
    
    This builder provides a chainable API for constructing elements
    with validation at each step.
    
    Example:
        >>> builder = ElementBuilder(schema_info)
        >>> element = (builder
        ...     .element("FileHeader")
        ...     .attr("revMajor", "1")
        ...     .attr("revMinor", "3")
        ...     .attr("date", "2025-10-12T00:00:00")
        ...     .attr("description", "My scenario")
        ...     .attr("author", "John Doe")
        ...     .build())
    """
    
    def __init__(self, schema_info: ISchemaInfo, strict: bool = True):
        """
        Initialize the builder with schema information.
        
        Args:
            schema_info: Parsed schema information
            strict: If True, validates during build
        """
        self.factory = ElementFactory(schema_info, strict)
        self._tag: Optional[str] = None
        self._attrs: Dict[str, str] = {}
        self._children: List[IElement] = []
    
    def element(self, tag: str) -> 'ElementBuilder':
        """
        Set the element tag name.
        
        Args:
            tag: Element tag name
        
        Returns:
            Self for chaining
        """
        self._tag = tag
        return self
    
    def attr(self, name: str, value: str) -> 'ElementBuilder':
        """
        Add an attribute.
        
        Args:
            name: Attribute name
            value: Attribute value
        
        Returns:
            Self for chaining
        """
        self._attrs[name] = value
        return self
    
    def attrs(self, attributes: Dict[str, str]) -> 'ElementBuilder':
        """
        Add multiple attributes at once.
        
        Args:
            attributes: Dictionary of attributes
        
        Returns:
            Self for chaining
        """
        self._attrs.update(attributes)
        return self
    
    def child(self, child: IElement) -> 'ElementBuilder':
        """
        Add a child element.
        
        Args:
            child: Child element to add
        
        Returns:
            Self for chaining
        """
        self._children.append(child)
        return self
    
    def children(self, children: List[IElement]) -> 'ElementBuilder':
        """
        Add multiple children at once.
        
        Args:
            children: List of child elements
        
        Returns:
            Self for chaining
        """
        self._children.extend(children)
        return self
    
    def build(self) -> IElement:
        """
        Build the element with validation.
        
        Returns:
            Created and validated element
        
        Raises:
            ValueError: If tag not set or validation fails
        """
        if not self._tag:
            raise ValueError("Element tag must be set before building")
        
        element = self.factory.create(
            self._tag,
            self._attrs,
            self._children
        )
        
        # Reset builder state
        self._tag = None
        self._attrs = {}
        self._children = []
        
        return element
    
    def build_with_defaults(self) -> IElement:
        """
        Build the element with required attributes auto-filled.
        
        Returns:
            Created element with defaults
        
        Raises:
            ValueError: If tag not set
        """
        if not self._tag:
            raise ValueError("Element tag must be set before building")
        
        element = self.factory.create_with_required_attrs(
            self._tag,
            self._attrs,
            auto_fill_defaults=True
        )
        
        # Add children after creation
        for child in self._children:
            element.add_child(child)
        
        # Reset builder state
        self._tag = None
        self._attrs = {}
        self._children = []
        
        return element
    
    def get_required_attrs(self) -> List[str]:
        """
        Get required attributes for current element tag.
        
        Returns:
            List of required attribute names
        
        Raises:
            ValueError: If tag not set
        """
        if not self._tag:
            raise ValueError("Element tag must be set")
        
        return self.factory.get_required_attributes(self._tag)
    
    def get_optional_attrs(self) -> List[str]:
        """
        Get optional attributes for current element tag.
        
        Returns:
            List of optional attribute names
        
        Raises:
            ValueError: If tag not set
        """
        if not self._tag:
            raise ValueError("Element tag must be set")
        
        return self.factory.get_optional_attributes(self._tag)
    
    def get_allowed_children(self) -> List[str]:
        """
        Get allowed child element names for current element tag.
        
        Returns:
            List of allowed child element names
        
        Raises:
            ValueError: If tag not set
        """
        if not self._tag:
            raise ValueError("Element tag must be set")
        
        return self.factory.get_allowed_children(self._tag)

