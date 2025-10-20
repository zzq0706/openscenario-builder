"""
XOSC Uniqueness Validator
Validates name uniqueness constraints within the scenario
"""

from typing import Dict, List, Optional

from openscenario_builder.interfaces import IElement, ISchemaInfo


class XoscUniquenessValidator:
    """Validates that element names are unique within their scope"""

    def validate(self, element: IElement, schema_info: Optional[ISchemaInfo] = None) -> List[str]:
        """
        Validate name uniqueness constraints
        
        Args:
            element: Root element to validate
            schema_info: Optional schema information (not used by this validator)
            
        Returns:
            List of validation error messages
        """
        errors = []
        errors.extend(self._validate_unique_element_names(element))
        return errors

    def _validate_unique_element_names(self, element: IElement) -> List[str]:
        """
        Validate that elements have unique names on the same level
        
        Args:
            element: Root element to validate
            
        Returns:
            List of validation errors
        """
        errors = []

        def validate_level(elem: IElement):
            # Track names and their occurrences at this level
            name_counts: Dict[str, List[IElement]] = {}

            for child in elem.children:
                if "name" in child.attrs:
                    name = child.attrs["name"]
                    if name in name_counts:
                        name_counts[name].append(child)
                    else:
                        name_counts[name] = [child]

            # Report duplicates
            for name, elements in name_counts.items():
                if len(elements) > 1:
                    element_tags = [e.tag for e in elements]
                    errors.append(
                        f"UNIQUENESS_ERROR: Duplicate name '{name}' found in {len(elements)} elements: "
                        f"{', '.join(element_tags)} under parent '{elem.tag}'. "
                        f"Fix: Ensure each element has a unique name within its parent scope."
                    )

            # Recursively validate children
            for child in elem.children:
                validate_level(child)

        validate_level(element)
        return errors
