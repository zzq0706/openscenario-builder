"""
XOSC Basic Structure Validator
Validates OpenSCENARIO document structure requirements
"""

from typing import List, Optional

from openscenario_builder.interfaces import IElement, ISchemaInfo


class XoscStructureValidator:
    """Validates basic OpenSCENARIO document structure requirements"""

    def validate(self, element: IElement, schema_info: Optional[ISchemaInfo] = None) -> List[str]:
        """
        Validate document structure
        
        Args:
            element: Root element to validate
            schema_info: Optional schema information (not used by this validator)
            
        Returns:
            List of validation error messages
        """
        errors = []
        errors.extend(self._validate_basic_structure(element))
        return errors

    def _validate_basic_structure(self, element: IElement) -> List[str]:
        """
        Validate basic OpenSCENARIO structure requirements
        
        Args:
            element: Root element to validate
            
        Returns:
            List of validation errors
        """
        errors = []

        # Check if this is the root OpenSCENARIO element
        if element.tag in ["OpenSCENARIO", "OpenScenario"]:
            errors.extend(self._validate_root_element(element))

        return errors

    def _validate_root_element(self, element: IElement) -> List[str]:
        """
        Validate the root OpenSCENARIO element structure
        
        Args:
            element: Root OpenSCENARIO element
            
        Returns:
            List of validation errors
        """
        errors = []

        # Check for required FileHeader
        fileheader_found = False
        for child in element.children:
            if child.tag == "FileHeader":
                fileheader_found = True
                errors.extend(self._validate_file_header(child))
                break

        if not fileheader_found:
            errors.append(
                "STRUCTURE_ERROR: FileHeader element is required in OpenSCENARIO. "
                "Fix: Add a FileHeader element as the first child of OpenSCENARIO."
            )

        # Check for major structural elements
        has_catalog_or_roadnetwork_or_entities = False
        has_storyboard = False

        for child in element.children:
            if child.tag in ["CatalogLocations", "RoadNetwork", "Entities"]:
                has_catalog_or_roadnetwork_or_entities = True
            elif child.tag == "Storyboard":
                has_storyboard = True

        # Optionally warn about missing common elements (not errors, but good practice)
        if not has_catalog_or_roadnetwork_or_entities:
            # This is informational, not an error
            pass

        if not has_storyboard:
            # This is informational for basic scenarios
            pass

        return errors

    def _validate_file_header(self, fileheader: IElement) -> List[str]:
        """
        Validate FileHeader element
        
        Args:
            fileheader: FileHeader element
            
        Returns:
            List of validation errors
        """
        errors = []

        # Check for required attributes
        required_attrs = ["revMajor", "revMinor", "date", "description"]
        for attr in required_attrs:
            if attr not in fileheader.attrs or not fileheader.attrs[attr]:
                errors.append(
                    f"STRUCTURE_ERROR: FileHeader is missing required attribute '{attr}'. "
                    f"Fix: Add '{attr}' attribute to FileHeader element."
                )

        return errors
