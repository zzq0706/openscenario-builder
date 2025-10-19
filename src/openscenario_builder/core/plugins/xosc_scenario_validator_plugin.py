"""
XOSC Scenario Validator Plugin for OpenSCENARIO Builder
Comprehensive validator that orchestrates specialized sub-validators

This is a refactored version (v3.1.0) that delegates to specialized validators:
- XoscSchemaStructureValidator: Element, attribute, and children validation
- XoscReferenceValidator: Entity, parameter, variable, and storyboard references
- XoscDataTypeValidator: Data type constraints and domain rules
- XoscStructureValidator: Document structure requirements
- XoscUniquenessValidator: Name uniqueness constraints
- XoscMinOccurValidator: Minimum occurrence constraints validation
"""

from typing import List, Optional
try:
    from .plugin_metadata import PluginMetadata
except ImportError:
    from openscenario_builder.core.plugins.plugin_metadata import PluginMetadata

from openscenario_builder.core.utils.validators import (
    XoscSchemaStructureValidator,
    XoscReferenceValidator,
    XoscDataTypeValidator,
    XoscStructureValidator,
    XoscUniquenessValidator,
    XoscMinOccurValidator,
)

from openscenario_builder.interfaces import IValidatorPlugin, IElement, ISchemaInfo


class XoscScenarioValidatorPlugin(IValidatorPlugin):
    """
    Comprehensive XOSC Scenario Validator Plugin
    
    This validator orchestrates multiple specialized validators to provide
    comprehensive validation of OpenSCENARIO scenarios. Each specialized
    validator focuses on a specific aspect of validation, making the system
    more maintainable, testable, and flexible.
    
    Architecture:
    - Schema structure validation (elements, attributes, children)
    - Reference validation (entities, parameters, variables, etc.)
    - Data type constraint validation
    - Document structure validation
    - Name uniqueness validation
    - Minimum occurrence constraint validation
    """

    def __init__(self):
        self._activated = True
        
        # Initialize specialized validators
        self._schema_validator = XoscSchemaStructureValidator()
        self._reference_validator = XoscReferenceValidator()
        self._datatype_validator = XoscDataTypeValidator()
        self._structure_validator = XoscStructureValidator()
        self._uniqueness_validator = XoscUniquenessValidator()
        self._min_occur_validator = XoscMinOccurValidator()

    @property
    def activated(self) -> bool:
        """Whether this plugin is activated and should be loaded"""
        return self._activated

    @activated.setter
    def activated(self, value: bool) -> None:
        """Set the activation state of this plugin"""
        self._activated = value

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="XOSC Scenario Comprehensive Validator",
            version="3.1.0",
            description="Comprehensive validator orchestrating specialized validators for schema, references, data types, structure, uniqueness, and occurrence constraints",
            author="Ziqi Zhou",
            tags=["validation", "schema", "xosc", "comprehensive"]
        )

    def validate(self, element: IElement, schema_info: Optional[ISchemaInfo] = None) -> List[str]:
        """
        Main validation method that orchestrates all specialized validators
        
        Runs validators in a specific order to optimize error detection:
        1. Schema structure - catches basic structural errors first
        2. Document structure - validates OpenSCENARIO requirements
        3. Minimum occurrence - validates required elements are present
        4. References - ensures all references can be resolved
        5. Data types - validates domain-specific constraints
        6. Uniqueness - checks name uniqueness constraints
        
        Args:
            element: Root element to validate
            schema_info: Schema information for validation
            
        Returns:
            List of all validation errors from all validators
        """
        errors = []

        # Run all specialized validators in order
        errors.extend(self._schema_validator.validate(element, schema_info))
        errors.extend(self._structure_validator.validate(element, schema_info))
        errors.extend(self._min_occur_validator.validate(element, schema_info))
        errors.extend(self._reference_validator.validate(element, schema_info))
        errors.extend(self._datatype_validator.validate(element, schema_info))
        errors.extend(self._uniqueness_validator.validate(element, schema_info))

        return errors

    def get_name(self) -> str:
        """Get the name of this validator plugin"""
        return self.metadata.name
