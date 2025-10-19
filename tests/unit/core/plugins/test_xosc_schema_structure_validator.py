"""
Unit tests for XOSC Schema Structure Validator
Tests XoscSchemaStructureValidator plugin
"""

import pytest
from openscenario_builder.core.utils.validators import XoscSchemaStructureValidator
from openscenario_builder.core.model.element import Element
from openscenario_builder.core.schema.parser import SchemaInfo, ElementDefinition, AttributeDefinition, GroupDefinition


class TestXoscSchemaStructureValidator:
    """Test Schema Structure Validator plugin"""

    def test_validate_without_schema_info(self):
        """Should return error when schema info is missing"""
        validator = XoscSchemaStructureValidator()
        element = Element("Test")
        
        errors = validator.validate(element, None)
        
        assert len(errors) == 1
        assert "CONFIGURATION_ERROR" in errors[0]
        assert "Schema information required" in errors[0]

    def test_validate_unknown_element(self):
        """Should return error for unknown element"""
        validator = XoscSchemaStructureValidator()
        element = Element("UnknownElement")
        schema_info = SchemaInfo(
            elements={},
            groups={},
            root_elements=[],
            element_hierarchy={},
            simple_type_definitions={}
        )
        
        errors = validator.validate(element, schema_info)
        
        assert len(errors) == 1
        assert "SCHEMA_ERROR" in errors[0]
        assert "UnknownElement" in errors[0]

    def test_validate_known_element(self):
        """Should not return error for known element"""
        validator = XoscSchemaStructureValidator()
        element = Element("TestElement")
        
        elem_def = ElementDefinition(
            name="TestElement",
            attributes=[],
            children=[]
        )
        schema_info = SchemaInfo(
            elements={"TestElement": elem_def},
            groups={},
            root_elements=[],
            element_hierarchy={},
            simple_type_definitions={}
        )
        
        errors = validator.validate(element, schema_info)
        
        assert len(errors) == 0

    def test_validate_unknown_attribute(self):
        """Should return error for unknown attribute"""
        validator = XoscSchemaStructureValidator()
        element = Element("TestElement", {"unknownAttr": "value"})
        
        elem_def = ElementDefinition(
            name="TestElement",
            attributes=[
                AttributeDefinition(name="validAttr", type="string", required=False)
            ],
            children=[]
        )
        schema_info = SchemaInfo(
            elements={"TestElement": elem_def},
            groups={},
            root_elements=[],
            element_hierarchy={},
            simple_type_definitions={}
        )
        
        errors = validator.validate(element, schema_info)
        
        assert len(errors) == 1
        assert "ATTRIBUTE_ERROR" in errors[0]
        assert "unknownAttr" in errors[0]

    def test_validate_missing_required_attribute(self):
        """Should return error for missing required attribute"""
        validator = XoscSchemaStructureValidator()
        element = Element("TestElement")
        
        elem_def = ElementDefinition(
            name="TestElement",
            attributes=[
                AttributeDefinition(name="requiredAttr", type="string", required=True)
            ],
            children=[]
        )
        schema_info = SchemaInfo(
            elements={"TestElement": elem_def},
            groups={},
            root_elements=[],
            element_hierarchy={},
            simple_type_definitions={}
        )
        
        errors = validator.validate(element, schema_info)
        
        assert len(errors) == 1
        assert "REQUIRED_ATTRIBUTE_ERROR" in errors[0]
        assert "requiredAttr" in errors[0]

    def test_validate_attribute_type_mismatch(self):
        """Should return error for invalid attribute type"""
        validator = XoscSchemaStructureValidator()
        element = Element("TestElement", {"intAttr": "not_a_number"})
        
        elem_def = ElementDefinition(
            name="TestElement",
            attributes=[
                AttributeDefinition(name="intAttr", type="int", required=False)
            ],
            children=[]
        )
        schema_info = SchemaInfo(
            elements={"TestElement": elem_def},
            groups={},
            root_elements=[],
            element_hierarchy={},
            simple_type_definitions={}
        )
        
        errors = validator.validate(element, schema_info)
        
        assert len(errors) == 1
        assert "TYPE_ERROR" in errors[0]
        assert "intAttr" in errors[0]

    def test_validate_attribute_with_parameter_reference(self):
        """Should accept parameter references for any type"""
        validator = XoscSchemaStructureValidator()
        element = Element("TestElement", {"intAttr": "$Speed"})
        
        elem_def = ElementDefinition(
            name="TestElement",
            attributes=[
                AttributeDefinition(name="intAttr", type="int", required=False)
            ],
            children=[]
        )
        schema_info = SchemaInfo(
            elements={"TestElement": elem_def},
            groups={},
            root_elements=[],
            element_hierarchy={},
            simple_type_definitions={}
        )
        
        errors = validator.validate(element, schema_info)
        
        assert len(errors) == 0

    def test_validate_enumerated_attribute_valid(self):
        """Should accept valid enumerated values"""
        validator = XoscSchemaStructureValidator()
        element = Element("TestElement", {"status": "active"})
        
        elem_def = ElementDefinition(
            name="TestElement",
            attributes=[
                AttributeDefinition(name="status", type="string", required=False)
            ],
            children=[]
        )
        schema_info = SchemaInfo(
            elements={"TestElement": elem_def},
            groups={},
            root_elements=[],
            element_hierarchy={},
            simple_type_definitions={"status": ["active", "inactive"]}
        )
        
        errors = validator.validate(element, schema_info)
        
        assert len(errors) == 0

    def test_validate_enumerated_attribute_invalid(self):
        """Should return error for invalid enumerated values"""
        validator = XoscSchemaStructureValidator()
        element = Element("TestElement", {"status": "unknown"})
        
        elem_def = ElementDefinition(
            name="TestElement",
            attributes=[
                AttributeDefinition(name="status", type="string", required=False)
            ],
            children=[]
        )
        schema_info = SchemaInfo(
            elements={"TestElement": elem_def},
            groups={},
            root_elements=[],
            element_hierarchy={},
            simple_type_definitions={"status": ["active", "inactive"]}
        )
        
        errors = validator.validate(element, schema_info)
        
        assert len(errors) == 1
        assert "VALUE_ERROR" in errors[0]
        assert "unknown" in errors[0]

    def test_validate_invalid_child_element(self):
        """Should return error for invalid child element"""
        validator = XoscSchemaStructureValidator()
        parent = Element("Parent")
        invalid_child = Element("InvalidChild")
        parent.add_child(invalid_child)
        
        parent_def = ElementDefinition(
            name="Parent",
            attributes=[],
            children=["ValidChild"]
        )
        schema_info = SchemaInfo(
            elements={
                "Parent": parent_def,
                "InvalidChild": ElementDefinition("InvalidChild", [], [])
            },
            groups={},
            root_elements=[],
            element_hierarchy={},
            simple_type_definitions={}
        )
        
        errors = validator.validate(parent, schema_info)
        
        assert len(errors) == 1
        assert "STRUCTURE_ERROR" in errors[0]
        assert "InvalidChild" in errors[0]

    def test_validate_valid_child_element(self):
        """Should accept valid child element"""
        validator = XoscSchemaStructureValidator()
        parent = Element("Parent")
        valid_child = Element("ValidChild")
        parent.add_child(valid_child)
        
        parent_def = ElementDefinition(
            name="Parent",
            attributes=[],
            children=["ValidChild"]
        )
        child_def = ElementDefinition(
            name="ValidChild",
            attributes=[],
            children=[]
        )
        schema_info = SchemaInfo(
            elements={
                "Parent": parent_def,
                "ValidChild": child_def
            },
            groups={},
            root_elements=[],
            element_hierarchy={},
            simple_type_definitions={}
        )
        
        errors = validator.validate(parent, schema_info)
        
        assert len(errors) == 0

    def test_validate_nested_elements(self):
        """Should validate nested element structures"""
        validator = XoscSchemaStructureValidator()
        root = Element("Root")
        child = Element("Child", {"requiredAttr": "value"})
        grandchild = Element("GrandChild")
        root.add_child(child)
        child.add_child(grandchild)
        
        root_def = ElementDefinition("Root", [], ["Child"])
        child_def = ElementDefinition(
            "Child",
            [AttributeDefinition("requiredAttr", "string", True)],
            ["GrandChild"]
        )
        grandchild_def = ElementDefinition("GrandChild", [], [])
        
        schema_info = SchemaInfo(
            elements={
                "Root": root_def,
                "Child": child_def,
                "GrandChild": grandchild_def
            },
            groups={},
            root_elements=[],
            element_hierarchy={},
            simple_type_definitions={}
        )
        
        errors = validator.validate(root, schema_info)
        
        assert len(errors) == 0

    def test_validate_with_group_reference(self):
        """Should expand and validate group references"""
        validator = XoscSchemaStructureValidator()
        parent = Element("Parent")
        child = Element("ChildA")
        parent.add_child(child)
        
        group = GroupDefinition("TestGroup", ["ChildA", "ChildB"])
        parent_def = ElementDefinition("Parent", [], ["GROUP:TestGroup"])
        child_def = ElementDefinition("ChildA", [], [])
        
        schema_info = SchemaInfo(
            elements={
                "Parent": parent_def,
                "ChildA": child_def
            },
            groups={"TestGroup": group},
            root_elements=[],
            element_hierarchy={},
            simple_type_definitions={}
        )
        
        errors = validator.validate(parent, schema_info)
        
        assert len(errors) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
