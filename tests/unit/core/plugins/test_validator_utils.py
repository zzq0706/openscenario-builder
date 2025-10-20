"""
Unit tests for validator utilities
Tests ValidationUtils, ElementCollector, and RecursiveValidator classes
"""

import pytest
from openscenario_builder.core.utils.validation_helpers import (
    ValidationUtils,
    ElementCollector,
    RecursiveValidator,
)
from openscenario_builder.core.model.element import Element
from openscenario_builder.core.schema.parser import SchemaInfo, GroupDefinition


class MockGroupDefinition(GroupDefinition):
    """Mock group definition for testing"""

    def __init__(self, children):
        super().__init__(name="MockGroup", children=children)


class TestValidationUtils:
    """Test ValidationUtils class"""

    def test_is_valid_attribute_value_with_valid_string(self):
        """Should return True for non-empty strings"""
        assert ValidationUtils.is_valid_attribute_value("value") is True
        assert ValidationUtils.is_valid_attribute_value("123") is True
        assert ValidationUtils.is_valid_attribute_value("test value") is True

    def test_is_valid_attribute_value_with_invalid_values(self):
        """Should return False for invalid values"""
        assert ValidationUtils.is_valid_attribute_value("") is False
        assert ValidationUtils.is_valid_attribute_value("   ") is False

    def test_is_valid_parameter_pattern_with_valid_patterns(self):
        """Should return True for valid parameter patterns"""
        assert ValidationUtils.is_valid_parameter_pattern("$Speed") is True
        assert ValidationUtils.is_valid_parameter_pattern("$_private") is True
        assert ValidationUtils.is_valid_parameter_pattern("$Var123") is True
        assert ValidationUtils.is_valid_parameter_pattern("$A") is True

    def test_is_valid_parameter_pattern_with_invalid_patterns(self):
        """Should return False for invalid parameter patterns"""
        assert ValidationUtils.is_valid_parameter_pattern("Speed") is False
        assert ValidationUtils.is_valid_parameter_pattern("$123") is False
        assert ValidationUtils.is_valid_parameter_pattern("$$Speed") is False
        assert ValidationUtils.is_valid_parameter_pattern("$Speed-1") is False
        assert ValidationUtils.is_valid_parameter_pattern("") is False

    def test_validate_attribute_type_string(self):
        """Should validate string type"""
        assert ValidationUtils.validate_attribute_type("any value", "string") is True
        assert ValidationUtils.validate_attribute_type("", "string") is True

    def test_validate_attribute_type_int(self):
        """Should validate int type"""
        assert ValidationUtils.validate_attribute_type("42", "int") is True
        assert ValidationUtils.validate_attribute_type("-10", "int") is True
        assert ValidationUtils.validate_attribute_type("0", "int") is True
        assert ValidationUtils.validate_attribute_type("3.14", "int") is False
        assert ValidationUtils.validate_attribute_type("abc", "int") is False

    def test_validate_attribute_type_unsigned_int(self):
        """Should validate unsignedInt type"""
        assert ValidationUtils.validate_attribute_type("42", "unsignedInt") is True
        assert ValidationUtils.validate_attribute_type("0", "unsignedInt") is True
        assert ValidationUtils.validate_attribute_type("-10", "unsignedInt") is False

    def test_validate_attribute_type_unsigned_short(self):
        """Should validate unsignedShort type"""
        assert ValidationUtils.validate_attribute_type("100", "unsignedShort") is True
        assert ValidationUtils.validate_attribute_type("0", "unsignedShort") is True
        assert ValidationUtils.validate_attribute_type("65535", "unsignedShort") is True
        assert (
            ValidationUtils.validate_attribute_type("65536", "unsignedShort") is False
        )
        assert ValidationUtils.validate_attribute_type("-1", "unsignedShort") is False

    def test_validate_attribute_type_double(self):
        """Should validate double/float type"""
        assert ValidationUtils.validate_attribute_type("3.14", "double") is True
        assert ValidationUtils.validate_attribute_type("42", "double") is True
        assert ValidationUtils.validate_attribute_type("-1.5", "float") is True
        assert ValidationUtils.validate_attribute_type("abc", "double") is False

    def test_validate_attribute_type_boolean(self):
        """Should validate boolean type"""
        assert ValidationUtils.validate_attribute_type("true", "boolean") is True
        assert ValidationUtils.validate_attribute_type("false", "boolean") is True
        assert ValidationUtils.validate_attribute_type("True", "boolean") is True
        assert ValidationUtils.validate_attribute_type("1", "boolean") is True
        assert ValidationUtils.validate_attribute_type("0", "boolean") is True
        assert ValidationUtils.validate_attribute_type("yes", "boolean") is False

    def test_validate_attribute_type_datetime(self):
        """Should validate dateTime type"""
        assert (
            ValidationUtils.validate_attribute_type("2023-12-01T10:30:00Z", "dateTime")
            is True
        )
        assert (
            ValidationUtils.validate_attribute_type("2023-12-01T10:30:00", "dateTime")
            is True
        )
        assert (
            ValidationUtils.validate_attribute_type("invalid-date", "dateTime") is False
        )

    def test_validate_attribute_type_with_parameters(self):
        """Should accept valid parameter references for any type"""
        assert ValidationUtils.validate_attribute_type("$Speed", "int") is True
        assert ValidationUtils.validate_attribute_type("$Value", "double") is True
        assert ValidationUtils.validate_attribute_type("$Flag", "boolean") is True
        assert (
            ValidationUtils.validate_attribute_type("$123", "int") is False
        )  # Invalid pattern

    def test_get_type_validation_hint(self):
        """Should return appropriate hints for types"""
        assert "decimal" in ValidationUtils.get_type_validation_hint("double")
        assert "whole number" in ValidationUtils.get_type_validation_hint("int")
        assert "positive" in ValidationUtils.get_type_validation_hint("unsignedInt")
        assert "true" in ValidationUtils.get_type_validation_hint("boolean")
        assert "ISO" in ValidationUtils.get_type_validation_hint("dateTime")

    def test_expand_children_with_groups_no_groups(self):
        """Should return children as-is when no groups"""
        groups = {}
        schema_info = SchemaInfo(
            elements={},
            groups=groups,
            root_elements=[],
            element_hierarchy={},
            simple_type_definitions={},
        )
        children = ["Element1", "Element2"]

        result = ValidationUtils.expand_children_with_groups(children, schema_info)

        assert result == children

    def test_expand_children_with_groups_simple_group(self):
        """Should expand group references"""
        groups = {"TestGroup": MockGroupDefinition(["Element1", "Element2"])}
        schema_info = SchemaInfo(
            elements={},
            groups=groups,
            root_elements=[],
            element_hierarchy={},
            simple_type_definitions={},
        )
        children = ["GROUP:TestGroup", "Element3"]

        result = ValidationUtils.expand_children_with_groups(children, schema_info)

        assert "Element1" in result
        assert "Element2" in result
        assert "Element3" in result
        assert "GROUP:TestGroup" not in result

    def test_expand_children_with_groups_nested(self):
        """Should expand nested group references"""
        groups = {
            "InnerGroup": MockGroupDefinition(["Element1", "Element2"]),
            "OuterGroup": MockGroupDefinition(["GROUP:InnerGroup", "Element3"]),
        }
        schema_info = SchemaInfo(
            elements={},
            groups=groups,
            root_elements=[],
            element_hierarchy={},
            simple_type_definitions={},
        )
        children = ["GROUP:OuterGroup"]

        result = ValidationUtils.expand_children_with_groups(children, schema_info)

        assert "Element1" in result
        assert "Element2" in result
        assert "Element3" in result


class TestElementCollector:
    """Test ElementCollector class"""

    def test_collect_by_tags_single_level(self):
        """Should collect elements with specified tags"""
        root = Element("Root")
        child1 = Element("Target", {"name": "entity1"})
        child2 = Element("Other", {"name": "other1"})
        root.add_child(child1)
        root.add_child(child2)

        result = ElementCollector.collect_by_tags(root, ["Target"])

        assert len(result) == 1
        assert "entity1" in result
        assert result["entity1"] == child1

    def test_collect_by_tags_nested(self):
        """Should collect elements recursively"""
        root = Element("Root")
        child = Element("Container")
        grandchild = Element("Target", {"name": "nested"})
        root.add_child(child)
        child.add_child(grandchild)

        result = ElementCollector.collect_by_tags(root, ["Target"])

        assert len(result) == 1
        assert "nested" in result

    def test_collect_by_tags_multiple_tags(self):
        """Should collect elements with any of the specified tags"""
        root = Element("Root")
        child1 = Element("Tag1", {"name": "elem1"})
        child2 = Element("Tag2", {"name": "elem2"})
        child3 = Element("Tag3", {"name": "elem3"})
        root.add_child(child1)
        root.add_child(child2)
        root.add_child(child3)

        result = ElementCollector.collect_by_tags(root, ["Tag1", "Tag2"])

        assert len(result) == 2
        assert "elem1" in result
        assert "elem2" in result
        assert "elem3" not in result

    def test_collect_entities(self):
        """Should collect entity elements"""
        root = Element("Root")
        entity1 = Element("ScenarioObject", {"name": "Ego"})
        entity2 = Element("Vehicle", {"name": "Car1"})
        root.add_child(entity1)
        root.add_child(entity2)

        result = ElementCollector.collect_entities(root)

        assert "Ego" in result
        assert "Car1" in result

    def test_collect_variables(self):
        """Should collect variable declarations"""
        root = Element("Root")
        var1 = Element("VariableDeclaration", {"name": "Speed"})
        var2 = Element("VariableDeclaration", {"name": "Distance"})
        root.add_child(var1)
        root.add_child(var2)

        result = ElementCollector.collect_variables(root)

        assert "Speed" in result
        assert "Distance" in result

    def test_collect_parameters(self):
        """Should collect parameter declarations"""
        root = Element("Root")
        param1 = Element("ParameterDeclaration", {"name": "InitSpeed"})
        param2 = Element("ParameterDeclaration", {"name": "MaxAccel"})
        root.add_child(param1)
        root.add_child(param2)

        result = ElementCollector.collect_parameters(root)

        assert "InitSpeed" in result
        assert "MaxAccel" in result

    def test_collect_storyboard_elements(self):
        """Should collect storyboard elements"""
        root = Element("Root")
        act = Element("Act", {"name": "Act1"})
        event = Element("Event", {"name": "Event1"})
        root.add_child(act)
        root.add_child(event)

        result = ElementCollector.collect_storyboard_elements(root)

        assert "Act1" in result
        assert "Event1" in result

    def test_collect_traffic_elements(self):
        """Should collect traffic signal controllers and signals"""
        root = Element("Root")
        controller = Element("TrafficSignalController", {"name": "Controller1"})
        signal = Element("TrafficSignal", {"id": "Signal1"})
        root.add_child(controller)
        root.add_child(signal)

        controllers, signals = ElementCollector.collect_traffic_elements(root)

        assert "Controller1" in controllers
        assert "Signal1" in signals

    def test_collect_elements_without_names(self):
        """Should skip elements without name attributes"""
        root = Element("Root")
        child1 = Element("ScenarioObject")  # No name
        child2 = Element("ScenarioObject", {"name": "WithName"})
        root.add_child(child1)
        root.add_child(child2)

        result = ElementCollector.collect_entities(root)

        assert len(result) == 1
        assert "WithName" in result


class TestRecursiveValidator:
    """Test RecursiveValidator class"""

    def test_traverse_and_validate_single_element(self):
        """Should validate single element"""
        root = Element("Root")

        def validation_func(elem):
            return [f"Error in {elem.tag}"]

        result = RecursiveValidator.traverse_and_validate(root, validation_func)

        assert len(result) == 1
        assert "Root" in result[0]

    def test_traverse_and_validate_with_children(self):
        """Should validate all elements in tree"""
        root = Element("Root")
        child1 = Element("Child1")
        child2 = Element("Child2")
        root.add_child(child1)
        root.add_child(child2)

        def validation_func(elem):
            return [f"Error in {elem.tag}"]

        result = RecursiveValidator.traverse_and_validate(root, validation_func)

        assert len(result) == 3
        assert any("Root" in err for err in result)
        assert any("Child1" in err for err in result)
        assert any("Child2" in err for err in result)

    def test_traverse_and_validate_with_args(self):
        """Should pass additional arguments to validation function"""
        root = Element("Root")

        def validation_func(elem, prefix):
            return [f"{prefix}: {elem.tag}"]

        result = RecursiveValidator.traverse_and_validate(
            root, validation_func, "ERROR"
        )

        assert len(result) == 1
        assert "ERROR: Root" in result[0]

    def test_traverse_and_validate_no_errors(self):
        """Should return empty list when no errors"""
        root = Element("Root")
        child = Element("Child")
        root.add_child(child)

        def validation_func(elem):
            return []

        result = RecursiveValidator.traverse_and_validate(root, validation_func)

        assert len(result) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
