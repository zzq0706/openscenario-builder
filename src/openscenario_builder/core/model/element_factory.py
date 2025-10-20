"""
Schema-Aware Element Factory for OpenSCENARIO Builder
Provides creation-time validation and type-safe element construction
"""

from typing import Dict, List, Optional, Set, Any
from openscenario_builder.interfaces import (
    ISchemaInfo,
    IElement,
    IElementDefinition,
    IChildElementInfo,
)
from openscenario_builder.core.model.element import Element

from openscenario_builder.core.utils.validators import (
    XoscSchemaStructureValidator,
    XoscDataTypeValidator,
    XoscStructureValidator,
)


class ElementFactory:
    """
    Factory for creating schema-validated elements.
    This factory reuses existing validators from core.utils.validators to ensure
    consistent validation across the codebase:
    - XoscSchemaStructureValidator: element structure, attributes, children
    - XoscDataTypeValidator: data types and enumerations
    - XoscStructureValidator: basic document structure
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
        # Track validation errors using element object as key
        self._validation_errors: Dict[IElement, List[str]] = {}
        # Initialize validators (reuse existing validation logic)
        self._schema_validator = XoscSchemaStructureValidator()
        self._datatype_validator = XoscDataTypeValidator()
        self._structure_validator = XoscStructureValidator()

    def create(
        self,
        tag: str,
        attrs: Optional[Dict[str, str]] = None,
        children: Optional[List[IElement]] = None,
        strict: Optional[bool] = None,
    ) -> IElement:
        """
        Create an element with schema validation using existing validators.

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

        # Create the element first
        element = Element(tag, attrs, children)

        # Reuse existing validators instead of custom validation logic
        errors = []

        # Schema structure validation (element exists, valid attributes, etc.)
        schema_errors = self._schema_validator.validate(element, self.schema_info)
        errors.extend(schema_errors)

        # Data type validation (type checking, enumerations)
        datatype_errors = self._datatype_validator.validate(element, self.schema_info)
        errors.extend(datatype_errors)

        # Basic structure validation
        structure_errors = self._structure_validator.validate(element, self.schema_info)
        errors.extend(structure_errors)

        # Handle errors based on strict mode
        if errors:
            if use_strict:
                raise ValueError(f"Validation failed for '{tag}': {'; '.join(errors)}")
            else:
                # Track validation errors using element object as key
                self._validation_errors[element] = errors

        return element

    def create_with_required_attrs(
        self,
        tag: str,
        attrs: Optional[Dict[str, str]] = None,
        auto_fill_defaults: bool = False,
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
            attr.name: {"type": attr.type, "required": attr.required}
            for attr in element_def.attributes
        }

    def validate_child_addition(self, parent_tag: str, child_tag: str) -> List[str]:
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
        return self._validation_errors.get(element, [])

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
            "description": getattr(element_def, "description", ""),
        }
