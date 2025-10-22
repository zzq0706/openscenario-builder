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

    def test_validate_expression_with_single_parameter(self):
        """Should validate expressions with single parameter and calculations"""
        validator = XoscReferenceValidator()
        root = Element("Root")
        param_decl = Element("ParameterDeclaration", {"name": "Ego_Start_Velocity"})
        action = Element("Action", {"speed": "${$Ego_Start_Velocity/3.6}"})
        root.add_child(param_decl)
        root.add_child(action)

        errors = validator.validate(root)

        assert len(errors) == 0

    def test_validate_expression_with_multiple_parameters(self):
        """Should validate expressions with multiple parameters and complex
        calculations"""
        validator = XoscReferenceValidator()
        root = Element("Root")
        param1 = Element(
            "ParameterDeclaration", {"name": "CrossingVehicle_InitDistance_m"}
        )
        param2 = Element("ParameterDeclaration", {"name": "P_CrossHead_m"})
        param3 = Element(
            "ParameterDeclaration", {"name": "CrossingVehicle_InitSpeed_mps"}
        )
        action = Element(
            "Action",
            {
                "value": (
                    "${($CrossingVehicle_InitDistance_m - $P_CrossHead_m) / "
                    "$CrossingVehicle_InitSpeed_mps}"
                )
            },
        )
        root.add_child(param1)
        root.add_child(param2)
        root.add_child(param3)
        root.add_child(action)

        errors = validator.validate(root)

        assert len(errors) == 0

    def test_validate_expression_with_missing_parameter(self):
        """Should error when parameter in expression doesn't exist"""
        validator = XoscReferenceValidator()
        root = Element("Root")
        param_decl = Element("ParameterDeclaration", {"name": "Ego_Start_Velocity"})
        action = Element("Action", {"speed": "${$Ego_Start_Velocity/$NonExistent}"})
        root.add_child(param_decl)
        root.add_child(action)

        errors = validator.validate(root)

        assert len(errors) == 1
        assert "REFERENCE_ERROR" in errors[0]
        assert "NonExistent" in errors[0]
        assert "expression" in errors[0].lower()

    def test_validate_expression_with_multiple_missing_parameters(self):
        """Should error for each missing parameter in complex expression"""
        validator = XoscReferenceValidator()
        root = Element("Root")
        param_decl = Element("ParameterDeclaration", {"name": "P_CrossHead_m"})
        action = Element(
            "Action", {"value": "${($Missing1 - $P_CrossHead_m) / $Missing2}"}
        )
        root.add_child(param_decl)
        root.add_child(action)

        errors = validator.validate(root)

        assert len(errors) == 2
        assert any("Missing1" in error for error in errors)
        assert any("Missing2" in error for error in errors)

    def test_validate_expression_with_operations(self):
        """Should validate expressions with various mathematical operations"""
        validator = XoscReferenceValidator()
        root = Element("Root")
        param1 = Element("ParameterDeclaration", {"name": "A"})
        param2 = Element("ParameterDeclaration", {"name": "B"})
        param3 = Element("ParameterDeclaration", {"name": "C"})
        # Test with +, -, *, /, parentheses, and decimal numbers
        action = Element("Action", {"value": "${($A + $B) * $C / 2.5 - 1.0}"})
        root.add_child(param1)
        root.add_child(param2)
        root.add_child(param3)
        root.add_child(action)

        errors = validator.validate(root)

        assert len(errors) == 0

    def test_extract_parameter_names_from_expression(self):
        """Should correctly extract parameter names from expressions"""
        validator = XoscReferenceValidator()

        # Test simple expression
        params = validator._extract_parameter_names_from_expression("${$Param1/3.6}")
        assert params == ["Param1"]

        # Test complex expression
        params = validator._extract_parameter_names_from_expression(
            "${($A - $B_Value) / $C_123}"
        )
        assert set(params) == {"A", "B_Value", "C_123"}

        # Test non-expression (should return empty list)
        params = validator._extract_parameter_names_from_expression("$SimpleParam")
        assert params == []

    def test_validate_literal_expression_no_parameters(self):
        """Should validate literal expressions without parameter references"""
        validator = XoscReferenceValidator()
        root = Element("Root")
        # No parameter declarations needed
        action = Element("Action", {"value": "${30/3.6}"})
        root.add_child(action)

        errors = validator.validate(root)

        assert len(errors) == 0

    def test_validate_complex_literal_expression(self):
        """Should validate complex literal expressions with various operations"""
        validator = XoscReferenceValidator()
        root = Element("Root")
        action = Element("Action", {"value": "${(100 - 30) / 15 + 2.5}"})
        root.add_child(action)

        errors = validator.validate(root)

        assert len(errors) == 0

    def test_validate_mixed_literal_and_parameter_expression(self):
        """Should validate expressions mixing literals and parameters"""
        validator = XoscReferenceValidator()
        root = Element("Root")
        param_decl = Element("ParameterDeclaration", {"name": "Speed"})
        action = Element("Action", {"value": "${$Speed + 10.5}"})
        root.add_child(param_decl)
        root.add_child(action)

        errors = validator.validate(root)

        assert len(errors) == 0

    def test_extract_no_parameters_from_literal_expression(self):
        """Should extract no parameters from literal expressions"""
        validator = XoscReferenceValidator()

        # Test various literal expressions
        test_cases = ["${30/3.6}", "${100 + 50}", "${(10 * 5) - 3.14}", "${1.5}"]

        for expression in test_cases:
            params = validator._extract_parameter_names_from_expression(expression)
            assert (
                params == []
            ), f"Expected no parameters for {expression}, got {params}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
