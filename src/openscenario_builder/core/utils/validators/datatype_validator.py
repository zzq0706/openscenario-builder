"""
XOSC Data Type Validator
Validates data type specific constraints and domain-specific rules
"""

from typing import List, Optional

from openscenario_builder.interfaces import IElement, ISchemaInfo


class XoscDataTypeValidator:
    """Validates data type constraints and domain-specific rules"""

    def validate(
        self, element: IElement, schema_info: Optional[ISchemaInfo] = None
    ) -> List[str]:
        """
        Validate data type constraints

        Args:
            element: Root element to validate
            schema_info: Optional schema information (not used by this validator)

        Returns:
            List of validation error messages
        """
        errors = []
        errors.extend(self._validate_special_data_types(element))
        return errors

    def _validate_special_data_types(self, element: IElement) -> List[str]:
        """
        Validate data type specific constraints

        Args:
            element: Root element to validate

        Returns:
            List of validation errors
        """
        errors = []

        def validate_recursive(elem: IElement):
            # Validate transition times (must be non-negative)
            if elem.tag == "LightStateAction" and "transitionTime" in elem.attrs:
                errors.extend(
                    self._validate_non_negative(
                        elem.attrs["transitionTime"],
                        "transitionTime",
                        "LightStateAction",
                    )
                )

            # Validate phase durations (must be positive)
            if elem.tag == "Phase" and "duration" in elem.attrs:
                errors.extend(
                    self._validate_positive(elem.attrs["duration"], "duration", "Phase")
                )

            # Validate speed values (should be non-negative)
            if "speed" in elem.attrs:
                errors.extend(
                    self._validate_non_negative(elem.attrs["speed"], "speed", elem.tag)
                )

            # Validate probability values (must be between 0 and 1)
            if "probability" in elem.attrs:
                errors.extend(
                    self._validate_probability(
                        elem.attrs["probability"], "probability", elem.tag
                    )
                )

            # Validate acceleration values (can be positive or negative)
            if "acceleration" in elem.attrs:
                errors.extend(
                    self._validate_numeric(
                        elem.attrs["acceleration"], "acceleration", elem.tag
                    )
                )

            # Validate distance values (should be non-negative)
            if "distance" in elem.attrs:
                errors.extend(
                    self._validate_non_negative(
                        elem.attrs["distance"], "distance", elem.tag
                    )
                )

            # Validate time values (should be non-negative)
            if "time" in elem.attrs and elem.tag != "AbsoluteTime":
                errors.extend(
                    self._validate_non_negative(elem.attrs["time"], "time", elem.tag)
                )

            # Recursively validate children
            for child in elem.children:
                validate_recursive(child)

        validate_recursive(element)
        return errors

    def _validate_non_negative(
        self, value: str, attr_name: str, element_tag: str
    ) -> List[str]:
        """
        Validate that a numeric value is non-negative

        Args:
            value: Value to validate
            attr_name: Attribute name
            element_tag: Element tag name

        Returns:
            List of validation errors (empty if valid)
        """
        # Skip parameter references
        if value.startswith("$"):
            return []

        try:
            num_value = float(value)
            if num_value < 0:
                return [
                    f"DATA_TYPE_ERROR: {attr_name.capitalize()} in {element_tag} must be non-negative, "
                    f"got '{value}'. Fix: Use a value >= 0."
                ]
        except ValueError:
            # Type validation is handled by schema structure validator
            pass

        return []

    def _validate_positive(
        self, value: str, attr_name: str, element_tag: str
    ) -> List[str]:
        """
        Validate that a numeric value is positive (> 0)

        Args:
            value: Value to validate
            attr_name: Attribute name
            element_tag: Element tag name

        Returns:
            List of validation errors (empty if valid)
        """
        # Skip parameter references
        if value.startswith("$"):
            return []

        try:
            num_value = float(value)
            if num_value <= 0:
                return [
                    f"DATA_TYPE_ERROR: {attr_name.capitalize()} in {element_tag} must be positive, "
                    f"got '{value}'. Fix: Use a value > 0."
                ]
        except ValueError:
            # Type validation is handled by schema structure validator
            pass

        return []

    def _validate_probability(
        self, value: str, attr_name: str, element_tag: str
    ) -> List[str]:
        """
        Validate that a probability value is between 0 and 1

        Args:
            value: Value to validate
            attr_name: Attribute name
            element_tag: Element tag name

        Returns:
            List of validation errors (empty if valid)
        """
        # Skip parameter references
        if value.startswith("$"):
            return []

        try:
            prob_value = float(value)
            if not (0 <= prob_value <= 1):
                return [
                    f"DATA_TYPE_ERROR: {attr_name.capitalize()} in {element_tag} must be between 0 and 1, "
                    f"got '{value}'. Fix: Use a value between 0.0 and 1.0."
                ]
        except ValueError:
            # Type validation is handled by schema structure validator
            pass

        return []

    def _validate_numeric(
        self, value: str, attr_name: str, element_tag: str
    ) -> List[str]:
        """
        Validate that a value is a valid numeric value (can be negative)

        Args:
            value: Value to validate
            attr_name: Attribute name
            element_tag: Element tag name

        Returns:
            List of validation errors (empty if valid)
        """
        # Skip parameter references
        if value.startswith("$"):
            return []

        try:
            float(value)
        except ValueError:
            # Type validation is handled by schema structure validator
            pass

        return []
