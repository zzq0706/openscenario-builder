"""
Type validation utilities for XOSC validators
Provides methods for validating attribute values against expected types
"""

from typing import List
from datetime import datetime
import re
from openscenario_builder.interfaces import ISchemaInfo, IGroupDefinition


class ValidationUtils:
    """Collection of reusable validation utility methods"""

    @staticmethod
    def is_valid_attribute_value(value: str) -> bool:
        """
        Check if an attribute value is valid (not None, not empty, not whitespace-only)

        Args:
            value: The attribute value to check

        Returns:
            True if value is valid, False otherwise
        """
        return value is not None and value != "" and value.strip() != ""

    @staticmethod
    def is_valid_parameter_pattern(value: str) -> bool:
        """
        Check if a value matches the OpenSCENARIO parameter pattern:
        [$][A-Za-z_][A-Za-z0-9_]*

        This pattern represents OpenSCENARIO parameters that start with a dollar sign
        followed by an identifier (letter or underscore, then letters, digits, or underscores)

        Args:
            value: The value to validate

        Returns:
            True if value matches parameter pattern, False otherwise
        """
        pattern = r"^\$[A-Za-z_][A-Za-z0-9_]*$"
        return bool(re.match(pattern, value))

    @staticmethod
    def validate_attribute_type(value: str, expected_type: str) -> bool:
        """
        Validate attribute value against expected type

        Args:
            value: The attribute value to validate
            expected_type: The expected data type (e.g., 'int', 'double', 'boolean')

        Returns:
            True if value matches expected type, False otherwise
        """
        if not value:
            return True

        # Parameters are valid for any type as they represent dynamic values
        if value.startswith("$"):
            return ValidationUtils.is_valid_parameter_pattern(value)

        try:
            if expected_type == "string":
                return True
            elif expected_type == "int":
                int(value)
                return True
            elif expected_type == "unsignedInt":
                val = int(value)
                return val >= 0
            elif expected_type == "unsignedShort":
                val = int(value)
                return 0 <= val <= 65535
            elif expected_type == "double" or expected_type == "float":
                float(value)
                return True
            elif expected_type == "boolean":
                return value.lower() in ("true", "false", "1", "0")
            elif expected_type == "dateTime":
                # Handle ISO format dates with or without timezone
                date_value = value
                if date_value.endswith("Z"):
                    date_value = date_value[:-1] + "+00:00"
                datetime.fromisoformat(date_value)
                return True
            else:
                # Unknown type, assume valid for extensibility
                return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def get_type_validation_hint(attr_type: str) -> str:
        """
        Get user-friendly validation hint for a given attribute type

        Args:
            attr_type: The attribute type

        Returns:
            User-friendly hint string
        """
        hints = {
            "double": "Use a decimal number (e.g., '1.0', '3.14').",
            "float": "Use a decimal number (e.g., '1.0', '3.14').",
            "int": "Use a whole number (e.g., '1', '42').",
            "unsignedInt": "Use a positive whole number (e.g., '0', '1', '42').",
            "unsignedShort": "Use a positive whole number between 0 and 65535.",
            "boolean": "Use 'true' or 'false'.",
            "dateTime": "Use ISO format (e.g., '2023-12-01T10:30:00Z').",
        }
        return hints.get(attr_type, f"Ensure value matches {attr_type} format.")

    @staticmethod
    def expand_children_with_groups(
        children: List[str], schema_info: ISchemaInfo
    ) -> List[str]:
        """
        Expand group references to get all valid child element names

        Args:
            children: List of child element names or group references
            schema_info: Schema information containing group definitions

        Returns:
            Expanded list of element names
        """
        expanded_children = []

        for child in children:
            if child.startswith("GROUP:"):
                group_name = child[6:]  # Remove "GROUP:" prefix
                group_def = schema_info.groups.get(group_name)
                if group_def:
                    expanded_children.extend(
                        ValidationUtils._expand_group_recursively(
                            group_def, schema_info
                        )
                    )
                else:
                    # Group not found, keep the reference for error reporting
                    expanded_children.append(child)
            else:
                expanded_children.append(child)

        return expanded_children

    @staticmethod
    def _expand_group_recursively(
        group_def: IGroupDefinition, schema_info: ISchemaInfo
    ) -> List[str]:
        """
        Recursively expand a group definition to get all valid element names

        Args:
            group_def: Group definition to expand
            schema_info: Schema information

        Returns:
            List of element names in the group
        """
        elements = []

        for child in group_def.children:
            if child.startswith("GROUP:"):
                nested_group_name = child[6:]
                nested_group_def = schema_info.groups.get(nested_group_name)
                if nested_group_def:
                    elements.extend(
                        ValidationUtils._expand_group_recursively(
                            nested_group_def, schema_info
                        )
                    )
            else:
                elements.append(child)

        return elements
