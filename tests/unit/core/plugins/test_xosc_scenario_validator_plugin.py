"""
Unit tests for XOSC Scenario Validator Plugin (Orchestrator)
Tests XoscScenarioValidatorPlugin that orchestrates all specialized validators
"""

import pytest
from openscenario_builder.core.plugins.xosc_scenario_validator_plugin import (
    XoscScenarioValidatorPlugin,
)
from openscenario_builder.core.model.element import Element
from openscenario_builder.core.schema.parser import (
    SchemaInfo,
    ElementDefinition,
    AttributeDefinition,
)


class TestXoscScenarioValidatorPlugin:
    """Test the main orchestrator validator plugin"""

    def test_plugin_metadata(self):
        """Should have proper metadata"""
        validator = XoscScenarioValidatorPlugin()

        assert validator.metadata.name == "XOSC Scenario Comprehensive Validator"
        assert validator.metadata.version == "3.2.0"
        assert validator.metadata.tags and "comprehensive" in validator.metadata.tags

    def test_activation_state(self):
        """Should support activation control"""
        validator = XoscScenarioValidatorPlugin()

        assert validator.activated is True
        validator.activated = False
        assert validator.activated is False

    def test_orchestrates_all_validators(self):
        """Should run all specialized validators"""
        validator = XoscScenarioValidatorPlugin()

        # Create a scenario with multiple types of errors
        root = Element("OpenSCENARIO")
        # Missing FileHeader (structure error)
        # Add invalid element (schema error)
        invalid_element = Element("InvalidElement")
        root.add_child(invalid_element)

        schema_info = SchemaInfo(
            elements={"OpenSCENARIO": ElementDefinition("OpenSCENARIO", [], [])},
            groups={},
            root_elements=[],
            element_hierarchy={},
            simple_type_definitions={},
        )

        errors = validator.validate(root, schema_info)

        # Should have errors from both structure and schema validators
        assert len(errors) >= 2
        assert any("FileHeader" in error for error in errors)
        assert any("InvalidElement" in error for error in errors)

    def test_schema_validation(self):
        """Should detect schema errors"""
        validator = XoscScenarioValidatorPlugin()
        element = Element("UnknownElement")

        schema_info = SchemaInfo(
            elements={},
            groups={},
            root_elements=[],
            element_hierarchy={},
            simple_type_definitions={},
        )

        errors = validator.validate(element, schema_info)

        assert len(errors) >= 1
        assert any("SCHEMA_ERROR" in error for error in errors)

    def test_reference_validation(self):
        """Should detect reference errors"""
        validator = XoscScenarioValidatorPlugin()
        root = Element("Root")
        action = Element("Action", {"entityRef": "NonExistent"})
        root.add_child(action)

        schema_info = SchemaInfo(
            elements={
                "Root": ElementDefinition("Root", [], ["Action"]),
                "Action": ElementDefinition(
                    "Action", [AttributeDefinition("entityRef", "string", False)], []
                ),
            },
            groups={},
            root_elements=[],
            element_hierarchy={},
            simple_type_definitions={},
        )

        errors = validator.validate(root, schema_info)

        assert len(errors) >= 1
        assert any("REFERENCE_ERROR" in error for error in errors)

    def test_datatype_validation(self):
        """Should detect data type errors"""
        validator = XoscScenarioValidatorPlugin()
        element = Element("Action", {"speed": "-10"})

        schema_info = SchemaInfo(
            elements={
                "Action": ElementDefinition(
                    "Action", [AttributeDefinition("speed", "double", False)], []
                )
            },
            groups={},
            root_elements=[],
            element_hierarchy={},
            simple_type_definitions={},
        )

        errors = validator.validate(element, schema_info)

        assert len(errors) >= 1
        assert any("DATA_TYPE_ERROR" in error for error in errors)

    def test_uniqueness_validation(self):
        """Should detect uniqueness errors"""
        validator = XoscScenarioValidatorPlugin()
        root = Element("Root")
        child1 = Element("Child", {"name": "duplicate"})
        child2 = Element("Child", {"name": "duplicate"})
        root.add_child(child1)
        root.add_child(child2)

        schema_info = SchemaInfo(
            elements={
                "Root": ElementDefinition("Root", [], ["Child"]),
                "Child": ElementDefinition(
                    "Child", [AttributeDefinition("name", "string", False)], []
                ),
            },
            groups={},
            root_elements=[],
            element_hierarchy={},
            simple_type_definitions={},
        )

        errors = validator.validate(root, schema_info)

        assert len(errors) >= 1
        assert any("UNIQUENESS_ERROR" in error for error in errors)

    def test_structure_validation(self):
        """Should detect structure errors"""
        validator = XoscScenarioValidatorPlugin()
        root = Element("OpenSCENARIO")
        # Missing FileHeader

        schema_info = SchemaInfo(
            elements={"OpenSCENARIO": ElementDefinition("OpenSCENARIO", [], [])},
            groups={},
            root_elements=[],
            element_hierarchy={},
            simple_type_definitions={},
        )

        errors = validator.validate(root, schema_info)

        assert len(errors) >= 1
        assert any("STRUCTURE_ERROR" in error for error in errors)

    def test_multiple_error_types(self):
        """Should detect multiple types of errors simultaneously"""
        validator = XoscScenarioValidatorPlugin()

        # Create a scenario with multiple error types
        root = Element("OpenSCENARIO")
        # Structure error: missing FileHeader

        # Add children with various errors
        child1 = Element("Child", {"name": "dup"})
        child2 = Element("Child", {"name": "dup"})  # Uniqueness error
        action = Element(
            "Action", {"speed": "-1", "entityRef": "Missing"}
        )  # Data type + reference errors

        root.add_child(child1)
        root.add_child(child2)
        root.add_child(action)

        schema_info = SchemaInfo(
            elements={
                "OpenSCENARIO": ElementDefinition(
                    "OpenSCENARIO", [], ["Child", "Action"]
                ),
                "Child": ElementDefinition(
                    "Child", [AttributeDefinition("name", "string", False)], []
                ),
                "Action": ElementDefinition(
                    "Action",
                    [
                        AttributeDefinition("speed", "double", False),
                        AttributeDefinition("entityRef", "string", False),
                    ],
                    [],
                ),
            },
            groups={},
            root_elements=[],
            element_hierarchy={},
            simple_type_definitions={},
        )

        errors = validator.validate(root, schema_info)

        # Should have at least 4 different types of errors
        assert len(errors) >= 4
        assert any("STRUCTURE_ERROR" in error for error in errors)
        assert any("UNIQUENESS_ERROR" in error for error in errors)
        assert any("DATA_TYPE_ERROR" in error for error in errors)
        assert any("REFERENCE_ERROR" in error for error in errors)

    def test_valid_scenario_no_errors(self):
        """Should return no errors for valid scenario"""
        validator = XoscScenarioValidatorPlugin()

        root = Element("OpenSCENARIO")
        fileheader = Element(
            "FileHeader",
            {
                "revMajor": "1",
                "revMinor": "3",
                "date": "2023-12-01T10:00:00",
                "description": "Test",
            },
        )
        root.add_child(fileheader)

        schema_info = SchemaInfo(
            elements={
                "OpenSCENARIO": ElementDefinition("OpenSCENARIO", [], ["FileHeader"]),
                "FileHeader": ElementDefinition(
                    "FileHeader",
                    [
                        AttributeDefinition("revMajor", "string", True),
                        AttributeDefinition("revMinor", "string", True),
                        AttributeDefinition("date", "string", True),
                        AttributeDefinition("description", "string", True),
                    ],
                    [],
                ),
            },
            groups={},
            root_elements=[],
            element_hierarchy={},
            simple_type_definitions={},
        )

        errors = validator.validate(root, schema_info)

        assert len(errors) == 0

    def test_get_name(self):
        """Should return validator name"""
        validator = XoscScenarioValidatorPlugin()

        name = validator.get_name()

        assert name == "XOSC Scenario Comprehensive Validator"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
