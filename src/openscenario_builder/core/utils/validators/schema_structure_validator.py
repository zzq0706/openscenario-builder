"""
XOSC Schema Structure Validator
Validates elements, attributes, and children against XOSC schema definitions
"""

from typing import Dict, List, Optional

from openscenario_builder.core.utils.validation_helpers import ValidationUtils

from openscenario_builder.interfaces import IElement, ISchemaInfo, IElementDefinition


class XoscSchemaStructureValidator:
    """Validates element structure, attributes, and children against schema"""

    def validate(
        self, element: IElement, schema_info: Optional[ISchemaInfo] = None
    ) -> List[str]:
        """
        Validate element structure against schema

        Args:
            element: Root element to validate
            schema_info: Schema information for validation

        Returns:
            List of validation error messages
        """
        if schema_info is None:
            return [
                "CONFIGURATION_ERROR: Schema information required for structure validation. "
                "Fix: Ensure OpenSCENARIO schema is properly loaded before validation."
            ]

        errors = []
        errors.extend(self._validate_element_recursively(element, schema_info))
        return errors

    def _validate_element_recursively(
        self, element: IElement, schema_info: ISchemaInfo
    ) -> List[str]:
        """
        Recursively validate an element and all its children against schema

        Args:
            element: Element to validate
            schema_info: Schema information

        Returns:
            List of validation errors
        """
        errors = []

        # Validate current element against schema
        element_errors = self._validate_element_against_schema(element, schema_info)
        errors.extend(element_errors)

        # Recursively validate all children
        for child in element.children:
            child_errors = self._validate_element_recursively(child, schema_info)
            errors.extend(child_errors)

        return errors

    def _validate_element_against_schema(
        self, element: IElement, schema_info: ISchemaInfo
    ) -> List[str]:
        """
        Validate a single element against the schema

        Args:
            element: Element to validate
            schema_info: Schema information

        Returns:
            List of validation errors
        """
        errors = []

        # Get element definition from schema
        element_def = schema_info.elements.get(element.tag)
        if not element_def:
            error_msg = (
                f"SCHEMA_ERROR: Unknown element '{element.tag}' is not defined in OpenSCENARIO schema. "
                f"Location: Element path contains '{element.tag}'. "
                f"Fix: Replace with a valid OpenSCENARIO element name."
            )
            errors.append(error_msg)
            return errors

        # Validate attributes
        errors.extend(
            self._validate_element_attributes(
                element, element_def, schema_info.simple_type_definitions
            )
        )

        # Validate children structure
        errors.extend(
            self._validate_element_children(element, element_def, schema_info)
        )

        return errors

    def _validate_element_attributes(
        self,
        element: IElement,
        element_def: IElementDefinition,
        simple_type_definitions: Dict[str, List[str]],
    ) -> List[str]:
        """
        Validate element attributes against schema definition

        Args:
            element: Element to validate
            element_def: Element definition from schema
            simple_type_definitions: Simple type definitions from schema

        Returns:
            List of validation errors
        """
        errors = []

        # Check for unknown attributes
        for attr_name in element.attrs.keys():
            if not any(attr.name == attr_name for attr in element_def.attributes):
                valid_attrs = [attr.name for attr in element_def.attributes]
                error_msg = (
                    f"ATTRIBUTE_ERROR: Unknown attribute '{attr_name}' for element '{element.tag}'. "
                    f"Valid attributes for '{element.tag}': {', '.join(valid_attrs)}. "
                    f"Fix: Remove '{attr_name}' or replace with a valid attribute name."
                )
                errors.append(error_msg)

        # Validate attribute values and check required attributes
        for attr_def in element_def.attributes:
            attr_name = attr_def.name
            attr_value = element.attrs.get(attr_name)

            # Check required attributes
            if attr_def.required and not ValidationUtils.is_valid_attribute_value(
                attr_value or ""
            ):
                attr_type = attr_def.type
                error_msg = (
                    f"REQUIRED_ATTRIBUTE_ERROR: Required attribute '{attr_name}' is missing, "
                    f"empty, or contains only whitespace for element '{element.tag}'. "
                    f"Expected type: {attr_type}. "
                    f"Fix: Add '{attr_name}=\"[appropriate_value]\"' to the '{element.tag}' element."
                )
                errors.append(error_msg)
                continue

            # Validate attribute type if value exists and is valid
            if attr_value and ValidationUtils.is_valid_attribute_value(attr_value):
                attr_type = attr_def.type

                # Skip parameter references for type validation
                if attr_value.startswith("$"):
                    continue

                if not ValidationUtils.validate_attribute_type(attr_value, attr_type):
                    error_msg = (
                        f"TYPE_ERROR: Invalid type for attribute '{attr_name}' in element '{element.tag}': "
                        f"expected {attr_type}, got '{attr_value}'. "
                        f"Fix: {ValidationUtils.get_type_validation_hint(attr_type)}"
                    )
                    errors.append(error_msg)

                # Validate against enumerated values if defined
                attr_key = next(
                    (
                        key
                        for key in simple_type_definitions.keys()
                        if key.lower() == attr_name.lower()
                    ),
                    None,
                )
                if attr_key:
                    if attr_value not in simple_type_definitions[attr_key]:
                        valid_values = simple_type_definitions[attr_key]
                        error_msg = (
                            f"VALUE_ERROR: Invalid value '{attr_value}' for attribute '{attr_name}' "
                            f"in element '{element.tag}'. "
                            f"Valid values: {', '.join(valid_values)}. "
                            f"Fix: Replace '{attr_value}' with one of the valid values."
                        )
                        errors.append(error_msg)

        return errors

    def _validate_element_children(
        self,
        element: IElement,
        element_def: IElementDefinition,
        schema_info: ISchemaInfo,
    ) -> List[str]:
        """
        Validate element children against schema definition

        Args:
            element: Element to validate
            element_def: Element definition from schema
            schema_info: Schema information

        Returns:
            List of validation errors
        """
        errors = []

        # Expand group references to get all valid child elements
        valid_children = ValidationUtils.expand_children_with_groups(
            element_def.children, schema_info
        )

        for child in element.children:
            if child.tag not in valid_children:
                error_msg = (
                    f"STRUCTURE_ERROR: Child element '{child.tag}' is not allowed in '{element.tag}'. "
                    f"Valid child elements for '{element.tag}': {', '.join(valid_children)}. "
                    f"Fix: Remove '{child.tag}' or replace with a valid child element."
                )
                errors.append(error_msg)

        return errors
