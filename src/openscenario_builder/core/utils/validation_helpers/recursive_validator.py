"""
Recursive validation utilities for XOSC validators
Provides base class and utilities for traversing element trees
"""

from typing import List
from openscenario_builder.interfaces import IElement


class RecursiveValidator:
    """Base class for validators that need to traverse the element tree"""

    @staticmethod
    def traverse_and_validate(
        root: IElement,
        validation_func,
        *args,
        **kwargs
    ) -> List[str]:
        """
        Traverse element tree and apply validation function to each element
        
        Args:
            root: Root element to start traversal from
            validation_func: Function to call on each element (receives elem as first arg)
            *args: Additional positional arguments to pass to validation_func
            **kwargs: Additional keyword arguments to pass to validation_func
            
        Returns:
            List of validation errors
        """
        errors = []

        def validate_recursive(elem: IElement):
            element_errors = validation_func(elem, *args, **kwargs)
            errors.extend(element_errors)

            for child in elem.children:
                validate_recursive(child)

        validate_recursive(root)
        return errors
