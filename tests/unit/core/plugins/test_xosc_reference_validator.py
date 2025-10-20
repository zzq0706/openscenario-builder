"""
Unit tests for XOSC Reference Validator
Tests XoscReferenceValidator plugin
"""

import pytest
from openscenario_builder.core.utils.validators import XoscReferenceValidator
from openscenario_builder.core.model.element import Element


class TestXoscReferenceValidator:
    """Test Reference Validator plugin"""

    def test_validate_entity_reference_exists(self):
        """Should not error when entity reference exists"""
        validator = XoscReferenceValidator()
        root = Element("Root")
        entity = Element("ScenarioObject", {"name": "Ego"})
        action = Element("Action", {"entityRef": "Ego"})
        root.add_child(entity)
        root.add_child(action)

        errors = validator.validate(root)

        assert len(errors) == 0

    def test_validate_entity_reference_missing(self):
        """Should error when entity reference doesn't exist"""
        validator = XoscReferenceValidator()
        root = Element("Root")
        action = Element("Action", {"entityRef": "NonExistent"})
        root.add_child(action)

        errors = validator.validate(root)

        assert len(errors) == 1
        assert "REFERENCE_ERROR" in errors[0]
        assert "NonExistent" in errors[0]
        assert "entityRef" in errors[0] or "entity" in errors[0].lower()

    def test_validate_entity_reference_with_parameter(self):
        """Should skip validation for parameter references"""
        validator = XoscReferenceValidator()
        root = Element("Root")
        action = Element("Action", {"entityRef": "$EntityName"})
        root.add_child(action)

        errors = validator.validate(root)

        assert len(errors) == 0

    def test_validate_variable_reference_exists(self):
        """Should not error when variable reference exists"""
        validator = XoscReferenceValidator()
        root = Element("Root")
        var_decl = Element("VariableDeclaration", {"name": "Speed"})
        var_action = Element("VariableAction", {"variableRef": "Speed"})
        root.add_child(var_decl)
        root.add_child(var_action)

        errors = validator.validate(root)

        assert len(errors) == 0

    def test_validate_variable_reference_missing(self):
        """Should error when variable reference doesn't exist"""
        validator = XoscReferenceValidator()
        root = Element("Root")
        var_action = Element("VariableAction", {"variableRef": "NonExistent"})
        root.add_child(var_action)

        errors = validator.validate(root)

        assert len(errors) == 1
        assert "REFERENCE_ERROR" in errors[0]
        assert "NonExistent" in errors[0]

    def test_validate_parameter_reference_exists(self):
        """Should not error when parameter reference exists"""
        validator = XoscReferenceValidator()
        root = Element("Root")
        param_decl = Element("ParameterDeclaration", {"name": "InitSpeed"})
        action = Element("Action", {"speed": "$InitSpeed"})
        root.add_child(param_decl)
        root.add_child(action)

        errors = validator.validate(root)

        assert len(errors) == 0

    def test_validate_parameter_reference_missing(self):
        """Should error when parameter reference doesn't exist"""
        validator = XoscReferenceValidator()
        root = Element("Root")
        action = Element("Action", {"speed": "$NonExistent"})
        root.add_child(action)

        errors = validator.validate(root)

        assert len(errors) == 1
        assert "REFERENCE_ERROR" in errors[0]
        assert "NonExistent" in errors[0]

    def test_validate_storyboard_reference_exists(self):
        """Should not error when storyboard element reference exists"""
        validator = XoscReferenceValidator()
        root = Element("Root")
        act = Element("Act", {"name": "Act1"})
        condition = Element("Condition", {"actRef": "Act1"})
        root.add_child(act)
        root.add_child(condition)

        errors = validator.validate(root)

        assert len(errors) == 0

    def test_validate_storyboard_reference_missing(self):
        """Should error when storyboard element reference doesn't exist"""
        validator = XoscReferenceValidator()
        root = Element("Root")
        condition = Element("Condition", {"actRef": "NonExistent"})
        root.add_child(condition)

        errors = validator.validate(root)

        assert len(errors) == 1
        assert "REFERENCE_ERROR" in errors[0]
        assert "NonExistent" in errors[0]

    def test_validate_traffic_signal_controller_reference_exists(self):
        """Should not error when traffic signal controller exists"""
        validator = XoscReferenceValidator()
        root = Element("Root")
        controller = Element("TrafficSignalController", {"name": "Controller1"})
        action = Element(
            "TrafficSignalStateAction", {"trafficSignalControllerRef": "Controller1"}
        )
        root.add_child(controller)
        root.add_child(action)

        errors = validator.validate(root)

        assert len(errors) == 0

    def test_validate_traffic_signal_controller_reference_missing(self):
        """Should error when traffic signal controller doesn't exist"""
        validator = XoscReferenceValidator()
        root = Element("Root")
        action = Element(
            "TrafficSignalStateAction", {"trafficSignalControllerRef": "NonExistent"}
        )
        root.add_child(action)

        errors = validator.validate(root)

        assert len(errors) == 1
        assert "REFERENCE_ERROR" in errors[0]
        assert "NonExistent" in errors[0]

    def test_validate_traffic_signal_id_exists(self):
        """Should not error when traffic signal ID exists"""
        validator = XoscReferenceValidator()
        root = Element("Root")
        signal = Element("TrafficSignal", {"id": "Signal1"})
        action = Element("TrafficSignalStateAction", {"signalId": "Signal1"})
        root.add_child(signal)
        root.add_child(action)

        errors = validator.validate(root)

        assert len(errors) == 0

    def test_validate_traffic_signal_id_missing(self):
        """Should error when traffic signal ID doesn't exist"""
        validator = XoscReferenceValidator()
        root = Element("Root")
        action = Element("TrafficSignalStateAction", {"signalId": "NonExistent"})
        root.add_child(action)

        errors = validator.validate(root)

        assert len(errors) == 1
        assert "REFERENCE_ERROR" in errors[0]
        assert "NonExistent" in errors[0]

    def test_validate_multiple_entity_types(self):
        """Should collect entities of different types"""
        validator = XoscReferenceValidator()
        root = Element("Root")
        vehicle = Element("Vehicle", {"name": "Car"})
        pedestrian = Element("Pedestrian", {"name": "Ped"})
        action1 = Element("Action", {"entityRef": "Car"})
        action2 = Element("Action", {"entityRef": "Ped"})
        root.add_child(vehicle)
        root.add_child(pedestrian)
        root.add_child(action1)
        root.add_child(action2)

        errors = validator.validate(root)

        assert len(errors) == 0

    def test_validate_nested_references(self):
        """Should validate references in nested elements"""
        validator = XoscReferenceValidator()
        root = Element("Root")
        entity = Element("ScenarioObject", {"name": "Ego"})
        parent = Element("Parent")
        child = Element("Child")
        action = Element("Action", {"entityRef": "Ego"})

        root.add_child(entity)
        root.add_child(parent)
        parent.add_child(child)
        child.add_child(action)

        errors = validator.validate(root)

        assert len(errors) == 0

    def test_validate_multiple_errors(self):
        """Should return all reference errors"""
        validator = XoscReferenceValidator()
        root = Element("Root")
        action1 = Element("Action", {"entityRef": "Missing1"})
        action2 = Element("Action", {"entityRef": "Missing2"})
        var_action = Element("VariableAction", {"variableRef": "Missing3"})
        root.add_child(action1)
        root.add_child(action2)
        root.add_child(var_action)

        errors = validator.validate(root)

        assert len(errors) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
