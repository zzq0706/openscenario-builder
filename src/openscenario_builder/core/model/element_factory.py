"""
Schema-Aware Element Factory for OpenSCENARIO Builder
Provides creation-time validation and type-safe element construction
"""

from typing import Dict, List, Optional, Set, Any
from openscenario_builder.interfaces import ISchemaInfo, IElement, IElementDefinition, IChildElementInfo
from openscenario_builder.core.model.element import Element


class ElementFactory:
    """
    Factory for creating schema-validated elements.
    
    This factory ensures that elements are created with:
    - Valid element names (must exist in schema)
    - Valid attributes (must be defined in schema)
    - Required attributes present (at creation or marked for later)
    - Type-correct attribute values
    
    Example:
        >>> factory = ElementFactory(schema_info)
        >>> # Strict mode - raises exception on invalid element
        >>> header = factory.create("FileHeader", {
        ...     "revMajor": "1",
        ...     "revMinor": "3",
        ...     "date": "2025-10-12T00:00:00",
        ...     "description": "My scenario",
        ...     "author": "John Doe"
        ... })
        >>> 
        >>> # Permissive mode - allows creation but tracks errors
        >>> element = factory.create("InvalidElement", strict=False)
        >>> errors = factory.get_validation_errors(element)
    """
    
    def __init__(self, schema_info: ISchemaInfo, strict: bool = True):
        """
        Initialize the factory with schema information.
        
        Args:
            schema_info: Parsed schema information
            strict: If True, raises exceptions on validation errors
                   If False, creates elements but tracks validation errors
        """
        self.schema_info = schema_info
        self.strict = strict
        # Use element's tag as key since id is not in IElement interface
        self._validation_errors: Dict[str, List[str]] = {}
    
    def create(
        self,
        tag: str,
        attrs: Optional[Dict[str, str]] = None,
        children: Optional[List[IElement]] = None,
        strict: Optional[bool] = None
    ) -> IElement:
        """
        Create an element with schema validation.
        
        Args:
            tag: Element tag name
            attrs: Element attributes
            children: Child elements
            strict: Override factory's strict mode for this creation
        
        Returns:
            Created element
        
        Raises:
            ValueError: If strict=True and validation fails
        """
        use_strict = strict if strict is not None else self.strict
        attrs = attrs or {}
        children = children or []
        
        errors = []
        
        # Validate element exists in schema
        element_def = self.schema_info.elements.get(tag)
        if not element_def:
            error = f"Element '{tag}' is not defined in schema"
            errors.append(error)
            if use_strict:
                raise ValueError(error)
        
        # Validate attributes if element definition exists
        if element_def:
            attr_errors = self._validate_attributes(tag, attrs, element_def)
            errors.extend(attr_errors)
            if use_strict and attr_errors:
                raise ValueError(f"Invalid attributes for '{tag}': {', '.join(attr_errors)}")
        
        # Create the element
        element = Element(tag, attrs, children)
        
        # Track validation errors for non-strict mode (using id from Element concrete class)
        if errors and hasattr(element, 'id'):
            self._validation_errors[element.id] = errors
        
        return element
    
    def create_with_required_attrs(
        self,
        tag: str,
        attrs: Optional[Dict[str, str]] = None,
        auto_fill_defaults: bool = False
    ) -> IElement:
        """
        Create an element and ensure all required attributes are present.
        
        Args:
            tag: Element tag name
            attrs: Element attributes
            auto_fill_defaults: If True, fills required attrs with empty strings
        
        Returns:
            Created element with required attributes
        
        Raises:
            ValueError: If required attributes are missing and auto_fill_defaults=False
        """
        attrs = attrs or {}
        element_def = self.schema_info.elements.get(tag)
        
        if not element_def:
            raise ValueError(f"Element '{tag}' is not defined in schema")
        
        # Check for required attributes
        required_attrs = [attr for attr in element_def.attributes if attr.required]
        missing_attrs = [attr.name for attr in required_attrs if attr.name not in attrs]
        
        if missing_attrs:
            if auto_fill_defaults:
                for attr_name in missing_attrs:
                    attrs[attr_name] = ""
            else:
                raise ValueError(
                    f"Element '{tag}' is missing required attributes: {', '.join(missing_attrs)}"
                )
        
        return self.create(tag, attrs)
    
    def get_allowed_children(self, tag: str) -> List[str]:
        """
        Get list of allowed child element names for a given element.
        
        Args:
            tag: Element tag name
        
        Returns:
            List of allowed child element names
        """
        element_def = self.schema_info.elements.get(tag)
        if not element_def:
            return []
        
        # children is List[str] according to IElementDefinition
        return list(element_def.children)
    
    def get_required_attributes(self, tag: str) -> List[str]:
        """
        Get list of required attribute names for a given element.
        
        Args:
            tag: Element tag name
        
        Returns:
            List of required attribute names
        """
        element_def = self.schema_info.elements.get(tag)
        if not element_def:
            return []
        
        return [attr.name for attr in element_def.attributes if attr.required]
    
    def get_optional_attributes(self, tag: str) -> List[str]:
        """
        Get list of optional attribute names for a given element.
        
        Args:
            tag: Element tag name
        
        Returns:
            List of optional attribute names
        """
        element_def = self.schema_info.elements.get(tag)
        if not element_def:
            return []
        
        return [attr.name for attr in element_def.attributes if not attr.required]
    
    def get_all_attributes(self, tag: str) -> Dict[str, Dict[str, Any]]:
        """
        Get all attribute definitions for an element.
        
        Args:
            tag: Element tag name
        
        Returns:
            Dictionary mapping attribute names to their definitions
            Format: {attr_name: {"type": str, "required": bool}}
        """
        element_def = self.schema_info.elements.get(tag)
        if not element_def:
            return {}
        
        return {
            attr.name: {
                "type": attr.type,
                "required": attr.required
            }
            for attr in element_def.attributes
        }
    
    def validate_child_addition(
        self,
        parent_tag: str,
        child_tag: str
    ) -> List[str]:
        """
        Validate if a child element can be added to a parent.
        
        Args:
            parent_tag: Parent element tag name
            child_tag: Child element tag name
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        parent_def = self.schema_info.elements.get(parent_tag)
        if not parent_def:
            errors.append(f"Parent element '{parent_tag}' not defined in schema")
            return errors
        
        # children is List[str] according to IElementDefinition
        allowed_children = list(parent_def.children)
        
        if child_tag not in allowed_children:
            errors.append(
                f"Element '{child_tag}' is not allowed as child of '{parent_tag}'. "
                f"Allowed children: {', '.join(allowed_children)}"
            )
        
        return errors
    
    def get_validation_errors(self, element: IElement) -> List[str]:
        """
        Get validation errors for an element created in non-strict mode.
        
        Args:
            element: Element to check
        
        Returns:
            List of validation errors
        """
        # Use element's id if available (from Element concrete class)
        element_id = getattr(element, 'id', None)
        if element_id:
            return self._validation_errors.get(element_id, [])
        return []
    
    def _validate_attributes(
        self,
        tag: str,
        attrs: Dict[str, str],
        element_def: IElementDefinition
    ) -> List[str]:
        """
        Validate element attributes against schema definition.
        
        Args:
            tag: Element tag name
            attrs: Attributes to validate
            element_def: Element definition from schema
        
        Returns:
            List of validation errors
        """
        errors = []
        
        # Get valid attribute names
        valid_attr_names = {attr.name for attr in element_def.attributes}
        
        # Check for invalid attributes
        for attr_name in attrs.keys():
            if attr_name not in valid_attr_names:
                errors.append(
                    f"Attribute '{attr_name}' is not valid for element '{tag}'. "
                    f"Valid attributes: {', '.join(sorted(valid_attr_names))}"
                )
        
        # Check for missing required attributes (warning, not error at creation)
        required_attrs = {attr.name for attr in element_def.attributes if attr.required}
        missing_required = required_attrs - set(attrs.keys())
        if missing_required:
            errors.append(
                f"Element '{tag}' is missing required attributes: {', '.join(sorted(missing_required))}"
            )
        
        # Validate attribute value types (basic validation)
        for attr_def in element_def.attributes:
            if attr_def.name in attrs:
                value = attrs[attr_def.name]
                type_errors = self._validate_attribute_type(
                    attr_def.name, value, attr_def.type
                )
                errors.extend(type_errors)
        
        return errors
    
    def _validate_attribute_type(
        self,
        attr_name: str,
        value: str,
        expected_type: str
    ) -> List[str]:
        """
        Validate attribute value type.
        
        Args:
            attr_name: Attribute name
            value: Attribute value
            expected_type: Expected type from schema
        
        Returns:
            List of validation errors
        """
        errors = []
        
        # Basic type validation
        if expected_type == "xs:double" or expected_type == "double":
            try:
                float(value)
            except ValueError:
                errors.append(
                    f"Attribute '{attr_name}' expects type 'double', got '{value}'"
                )
        
        elif expected_type == "xs:int" or expected_type == "int":
            try:
                int(value)
            except ValueError:
                errors.append(
                    f"Attribute '{attr_name}' expects type 'int', got '{value}'"
                )
        
        elif expected_type == "xs:boolean" or expected_type == "boolean":
            if value.lower() not in ["true", "false", "1", "0"]:
                errors.append(
                    f"Attribute '{attr_name}' expects type 'boolean', got '{value}'"
                )
        
        # Check enumeration values
        if expected_type in self.schema_info.simple_type_definitions:
            valid_values = self.schema_info.simple_type_definitions[expected_type]
            if valid_values and value not in valid_values:
                errors.append(
                    f"Attribute '{attr_name}' value '{value}' not in allowed values: "
                    f"{', '.join(valid_values)}"
                )
        
        return errors
    
    def get_element_info(self, tag: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive information about an element from schema.
        
        Args:
            tag: Element tag name
        
        Returns:
            Dictionary with element information or None if not found
        """
        element_def = self.schema_info.elements.get(tag)
        if not element_def:
            return None
        
        return {
            "name": tag,
            "attributes": self.get_all_attributes(tag),
            "required_attributes": self.get_required_attributes(tag),
            "optional_attributes": self.get_optional_attributes(tag),
            "allowed_children": self.get_allowed_children(tag),
            "description": getattr(element_def, "description", "")
        }
